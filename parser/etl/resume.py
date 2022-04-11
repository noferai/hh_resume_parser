import re
import typing
from collections import defaultdict

import funcy as fc
from langdetect import DetectorFactory, detect_langs

import parser.models as models
from config import logger, LanguageError
from parser.constants import SECTION_TITLE_MAX, show_more
from parser.converters.docx import get_paragraphs
from .fields import FieldsExtractor
from .notion import NotionConverter


def slice_raw(func):
    def wrapper(self, raw):
        return func(self, raw[1:])

    return wrapper


class ResumeETL:
    def __init__(self, file: typing.IO[bytes]):
        self.raw_paragraphs = get_paragraphs(file)
        self.template_lang, self.doc_lang = self.detect_language()
        self.filter_paragraphs()
        self.sections = self.fetch_sections(self.template_lang)
        self.populate_sections_raw()
        self.fields = FieldsExtractor(self.template_lang, self.doc_lang)

    def detect_language(self) -> typing.Tuple[str, str]:
        DetectorFactory.seed = 0
        ru_sections, en_sections = self.fetch_sections("ru"), self.fetch_sections("en")
        if len(ru_sections) > len(en_sections):
            template_lang = "ru"
            sections = [title for _, v in ru_sections.items() if len((title := v["title"])) > 0]
        else:
            template_lang = "en"
            sections = [title for _, v in en_sections.items() if len((title := v["title"])) > 0]

        content = " ".join(
            [p for p in fc.flatten(self.raw_paragraphs) if not any(re.match(str(s), p) for s in sections)]
        )
        doc_lang = None
        for _l in detect_langs(content):
            if _l.lang == "ru" or _l.lang == "en":
                doc_lang = _l.lang
                break
        if not doc_lang:
            raise LanguageError
        return template_lang, doc_lang

    def filter_paragraphs(self):
        def predicate(item: str) -> bool:
            if show_more[self.template_lang] in fc.str_join(item):
                return False
            return True

        self.raw_paragraphs = fc.lfilter(lambda i: predicate(i), self.raw_paragraphs)

    def fetch_sections(self, lang: str) -> dict:
        """Returns sections presented in current resume"""
        sections = defaultdict()
        sections["general"] = {"title": "", "index": (curr_index := 0)}

        sections_re = {k: v.re(lang) for k, v in models.all_sections.items()}
        for k, v in sections_re.items():
            for i, par in enumerate(self.raw_paragraphs):
                if len(par_flat := fc.str_join(par)) < SECTION_TITLE_MAX:
                    if re.search(fr"{v['title']}", par_flat, re.IGNORECASE) and i > curr_index:
                        sections[k] = {"title": v["title"], "index": i}
                        curr_index = i

        return sections

    def populate_sections_raw(self):
        """Populates sections with raw content"""
        for s, s_next in fc.with_next(self.sections.items()):
            i_next = s_next[1]["index"] if s_next else len(self.raw_paragraphs)
            self.sections[s[0]]["raw"] = self.raw_paragraphs[s[1]["index"] : i_next]

    def get_general(self, raw: list) -> models.General:
        if "сайте" in raw[0]:
            raw.pop(0)
        if self.fields.extract("gender", raw[0]):
            name = None
        else:
            name = raw.pop(0)
        section = models.General(
            name=name,
            gender=self.fields.extract("gender", raw),
            age=self.fields.extract("age", raw),
            birthday=self.fields.extract("birthday", raw),
        )
        return section

    @slice_raw
    def get_contacts(self, raw: list) -> models.Contacts:
        _raw = fc.lflatten(raw)
        section = models.Contacts(
            emails=[i for p in _raw if (i := self.fields.extract("email", p))],
            phones=[i for p in _raw if (i := self.fields.extract("phone", p))],
            links=[i for p in _raw if (i := self.fields.extract("link", p))],
            location=self.fields.extract("location", fc.last(raw)),
        )
        return section

    def get_position(self, raw: list) -> models.Position:
        section = models.Position(
            updated=self.fields.extract("updated", raw.pop(0)),
            name=raw.pop(0),
            salary=self.fields.extract("salary", fc.first(raw)),
        )
        return section

    def get_experience(self, raw: list) -> models.Experience:
        section = models.Experience(
            total=self.fields.extract("experience.total", raw.pop(0)),
            items=self.fields.extract("experience.items", raw),
        )
        return section

    @slice_raw
    def get_skills(self, raw: list) -> models.Skills:
        section = models.Skills(items=fc.flatten(raw))
        return section

    @slice_raw
    def get_driving(self, raw: list) -> models.Driving:
        section = models.Driving(
            own_car=self.fields.extract("own_car", raw),
            categories=self.fields.extract("driving_categories", raw),
        )
        return section

    @slice_raw
    def get_about(self, raw: list) -> models.About:
        return models.About(text=raw[0])

    @slice_raw
    def get_recommendations(self, raw: list) -> models.Recommendations:
        return models.Recommendations(items=raw)

    @staticmethod
    def get_portfolio(raw: list):
        pass

    def get_education(self, raw: list) -> models.Education:
        section = models.Education(
            degree=self.fields.extract("degree", raw.pop(0)), items=self.fields.extract("education.items", raw)
        )
        return section

    @slice_raw
    def get_languages(self, raw: list) -> models.Languages:
        section = models.Languages(items=self.fields.extract("languages.items", raw))
        return section

    @slice_raw
    def get_certificates(self, raw: list) -> models.Certificates:
        section = models.Certificates(other=raw)
        return section

    @slice_raw
    def get_additional_edu(self, raw: list) -> models.AdditionalEducation:
        section = models.AdditionalEducation(items=self.fields.extract("additional_edu.items", raw))
        return section

    @slice_raw
    def get_tests(self, raw: list) -> models.Tests:
        section = models.Tests(items=self.fields.extract("additional_edu.items", raw))
        return section

    @slice_raw
    def get_citizenship(self, raw: list) -> models.Citizenship:
        section = models.Citizenship(**self.fields.extract("citizenship", raw))
        return section

    def get_section(self, attr_name: str, data: list):
        try:
            getter = getattr(self, f"get_{attr_name}")
            return getter(data)
        except AttributeError:
            logger.error(f"No getter method for <{attr_name}> attribute found")

    def get_resume(self) -> dict:
        """Returns resume as dict of sections"""
        resume = defaultdict()
        for name, content in self.sections.items():
            raw = content.get("raw")
            if section := self.get_section(name, raw):
                resume[name] = section.dict()
        return resume

    def to_notion(self) -> dict:
        f_sections = self.get_resume()
        notion_page = NotionConverter(f_sections, self.template_lang).convert_resume()
        return notion_page
