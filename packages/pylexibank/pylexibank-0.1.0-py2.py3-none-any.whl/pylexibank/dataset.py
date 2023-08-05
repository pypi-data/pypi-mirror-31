# coding: utf8
from __future__ import unicode_literals, print_function, division
import logging
from datetime import datetime

import attr
import six
from clldutils.dsv import reader
from clldutils.text import split_text_with_context, strip_brackets
from clldutils.misc import lazyproperty
from clldutils.loglib import Logging
from clldutils.path import remove, rmtree, write_text
from clldutils import licenses
from clldutils import jsonlib
from pyglottolog.languoids import Glottocode

from lingpy.settings import rc
from segments.tokenizer import Tokenizer

import pylexibank
from pylexibank.util import get_variety_id, DataDir
from pylexibank import cldf

NOOP = -1


def non_empty(_, attribute, value):
    if not value:
        raise ValueError('{0} must be non-empty'.format(attribute))


class FieldnamesMixin(object):
    @classmethod
    def fieldnames(cls):
        return [f.name for f in attr.fields(cls)]


@attr.s(hash=False)
class Language(FieldnamesMixin):
    ID = attr.ib(default='', hash=True)
    name = attr.ib(default=None)
    iso = attr.ib(default=None)
    glottocode = attr.ib(default=None)
    glottolog_name = attr.ib(default=None)
    macroarea = attr.ib(default=None)
    family = attr.ib(default=None)

    @classmethod
    def __cldf_table__(cls):
        return 'LanguageTable'


@attr.s(hash=False)
class Concept(FieldnamesMixin):
    ID = attr.ib(default='', hash=True)
    gloss = attr.ib(default='')
    conceptset = attr.ib(default='')
    concepticon_gloss = attr.ib(default='')

    @classmethod
    def __cldf_table__(cls):
        return 'ParameterTable'


@attr.s
class Lexeme(FieldnamesMixin):
    """
    Raw lexical data item as it can be pulled out of the original datasets.

    This is the basis for creating rows in CLDF representations of the data by
    - splitting the lexical item into forms
    - cleaning the forms
    - potentially tokenizing the form
    """
    ID = attr.ib()
    Form = attr.ib()
    Value = attr.ib(validator=non_empty)  # the lexical item
    Language_ID = attr.ib(validator=non_empty)
    Parameter_ID = attr.ib(validator=non_empty)
    Local_ID = attr.ib(default=None)
    Segments = attr.ib(
        default=attr.Factory(list),
        validator=attr.validators.instance_of(list))
    Source = attr.ib(
        default=attr.Factory(list),
        validator=attr.validators.instance_of(list),
        convert=lambda v: [v] if isinstance(v, six.string_types) else v)
    Comment = attr.ib(default=None)
    Cognacy = attr.ib(default=None)
    Loan = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(bool)))

    @classmethod
    def __cldf_table__(cls):
        return 'FormTable'


@attr.s
class Cognate(FieldnamesMixin):
    Word_ID = attr.ib(default=None)  # The lexibank-wide unique word ID.
    Index = attr.ib(default=None)  # integer index used in lingpy wordlists.
    Form = attr.ib(default=None)
    Cognateset_ID = attr.ib(default=None)
    Doubt = attr.ib(
        default=False, convert=lambda v: v if isinstance(v, bool) else eval(v))
    Cognate_detection_method = attr.ib(default='expert')
    Cognate_source = attr.ib(default=None)
    Alignment = attr.ib(
        default=None, convert=lambda v: ' '.join(v) if isinstance(v, list) else v)
    Alignment_method = attr.ib(default=None)
    Alignment_source = attr.ib(default=None)

    @classmethod
    def __cldf_table__(cls):
        return 'CognateTable'


@attr.s
class Metadata(object):
    title = attr.ib(default=None)
    description = attr.ib(default=None)
    citation = attr.ib(default=None)
    license = attr.ib(default=None)
    url = attr.ib(default=None)
    aboutUrl = attr.ib(default=None)
    conceptlist = attr.ib(default=None)
    lingpy_schema = attr.ib(default=None)
    derived_from = attr.ib(default=None)
    related = attr.ib(default=None)
    source = attr.ib(default=None)

    @property
    def common_props(self):
        return {
            "dc:title": self.title,
            "dc:description": self.description,
            "dc:bibliographicCitation": self.citation,
            "dc:license": licenses.find(self.license) if self.license else None,
            "dc:identifier": self.url,
            "dc:format": "http://concepticon.clld.org/contributions/{0}".format(
                self.conceptlist) if self.conceptlist else None,
            "dc:isVersionOf": "http://lexibank.clld.org/contributions/{0}".format(
                self.derived_from) if self.derived_from else None,
            "dc:related": self.related,
            "aboutUrl": self.aboutUrl,
        }


class Dataset(object):
    """
    A lexibank dataset.

    This object provides access to a dataset's
    - language list as attribute `languages`
    - concept list as attribute `concepts`
    - concepticon concept-list ID as attribute `conceptlist`
    """
    dir = None  # Derived classes must provide an existing directory here!
    lexeme_class = Lexeme
    cognate_class = Cognate
    language_class = Language
    concept_class = Concept
    log = logging.getLogger(pylexibank.__name__)

    @lazyproperty
    def id(self):
        return self.dir.name

    @lazyproperty
    def metadata(self):
        return Metadata(**jsonlib.load(self.dir / 'metadata.json'))

    @property
    def stats(self):
        if self.dir.joinpath('README.json').exists():
            return jsonlib.load(self.dir.joinpath('README.json'))
        return {}

    def __init__(self, concepticon=None, glottolog=None):
        self.unmapped = Unmapped()
        self.dir = DataDir(self.dir)

        # raw data, either downloaded or commited to the repository
        self.raw = DataDir(self.dir.joinpath('raw'))

        # cldf directory
        self.cldf_dir = self.dir.joinpath('cldf')

        # languages
        self.languages = []
        lpath = self.dir / 'etc' / 'languages.csv'
        if lpath.exists():
            for item in reader(lpath, dicts=True):
                if item.get('GLOTTOCODE', None) and not \
                        Glottocode.pattern.match(item['GLOTTOCODE']):  # pragma: no cover
                    raise ValueError(
                        "Wrong glottocode for item {0}".format(item['GLOTTOCODE']))
                self.languages.append(item)

        # concepts
        self.conceptlist = {}
        self.concepts = []
        cpath = self.dir / 'etc' / 'concepts.csv'
        if cpath.exists():
            self.concepts = list(reader(cpath, dicts=True))

        # sources
        self.sources = []
        spath = self.dir / 'etc' / 'sources.csv'
        if spath.exists():
            self.sources = list(reader(spath, dicts=True))
            
        self.lexemes = {}
        lpath = self.dir / 'etc' / 'lexemes.csv'
        if lpath.exists():
            for item in reader(lpath, dicts=True):
                self.lexemes[item['LEXEME']] = item['REPLACEMENT']

        # glottolog and concepticon
        self.glottolog = glottolog
        self.concepticon = concepticon

    def debug(self):
        return Logging(self.log)

    # ---------------------------------------------------------------
    # workflow actions whih should be overwritten by derived classes:
    # ---------------------------------------------------------------
    def cmd_download(self, **kw):
        self._not_implemented('download')
        return NOOP

    def cmd_install(self, **kw):
        self._not_implemented('install')
        return NOOP

    # ---------------------------------------------------------------
    # handling of lexemes/forms/words
    # ---------------------------------------------------------------
    def clean_form(self, item, form):
        """
        Called when a row is added to a CLDF dataset.

        :param form:
        :return: None to skip the form, or the cleaned form as string.
        """
        form = strip_brackets(form)
        if form not in ['?']:
            return form

    def split_forms(self, item, value):
        value = self.lexemes.get(value, value)
        return [self.clean_form(item, form)
                for form in split_text_with_context(value, separators='/,;')]

    def get_tokenizer(self):
        profile = self.dir.joinpath('orthography.tsv')
        if profile.exists():
            obj = Tokenizer(profile=profile.as_posix())

            def _tokenizer(item, string, **kw):
                kw.setdefault("column", "IPA")
                kw.setdefault("separator", " _ ")
                return obj(string, **kw).split()
            return _tokenizer

    # ---------------------------------------------------------------
    # CLDF dataset access
    # ---------------------------------------------------------------
    @property
    def cldf(self):
        return cldf.Dataset(self)

    # ---------------------------------------------------------------
    def _download(self, **kw):
        if not self.raw.exists():
            self.raw.mkdir()

        self.cmd_download(**kw)
        write_text(
            self.raw / 'README.md',
            'Raw data downloaded {0}'.format(datetime.utcnow().isoformat()))

    def _install(self, **kw):
        if not self.cldf_dir.exists():
            self.cldf_dir.mkdir()

        self.unmapped.clear()

        if self.metadata.conceptlist:
            self.conceptlist = self.concepticon.conceptlists[self.metadata.conceptlist]
        rc(schema=self.metadata.lingpy_schema or 'ipa')
        if self.cmd_install(**kw) != NOOP:
            if kw.get('verbose'):
                self.unmapped.pprint()
            self.cldf.validate(kw['log'])

    def _clean(self, **kw):
        self.log.debug('removing CLDF directory %s' % self.cldf_dir)
        if self.cldf_dir.exists():
            for f in self.cldf_dir.iterdir():
                if f.is_file():
                    remove(f)
                else:
                    rmtree(f)

    def _not_implemented(self, method):
        self.log.warn('cmd_{0} not implemented for dataset {1}'.format(method, self.id))

    @lazyproperty
    def _tokenizer(self):
        return self.get_tokenizer()

    def _segment(self, item, string):
        if self._tokenizer:
            return self._tokenizer(item, string)

    def coverage(self, vars, glangs, c):  # pragma: no cover
        for row in self.cldf['FormTable']:
            try:
                cid = int(row['Parameter_ID'])
            except (ValueError, TypeError):
                continue
            vid = self.id + '-' + get_variety_id(row)
            c[cid].add(vid)
            vars[vid].add(cid)
            glangs[row['Language_ID']].add(cid)


class Unmapped(object):
    def __init__(self):
        self.languages = set()
        self.concepts = set()

    def clear(self):
        self.languages = set()
        self.concepts = set()

    def add_concept(self, **kw):
        kw['ID'] = kw.pop('id')
        self.concepts.add(Concept(**kw))

    def add_language(self, **kw):
        kw['ID'] = kw.pop('id')
        self.languages.add(Language(**kw))

    @staticmethod
    def quote(v):
        v = '{0}'.format(v or '')
        if ',' in v or len(v.split()) > 1:
            v = '"%s"' % v.replace('"', '""')
        return v

    def pprint(self):
        for objs, cls in [(self.languages, Language), (self.concepts, Concept)]:
            if objs:
                print('=== Unmapped %ss ===' % cls.__name__)
                print(','.join([a.name.upper() for a in attr.fields(cls)]))
                for row in sorted(map(attr.astuple, objs)):
                    print(','.join(map(self.quote, row)))
