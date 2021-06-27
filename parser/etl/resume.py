import re
import typing

from collections import defaultdict
from langdetect import DetectorFactory, detect_langs
from parser.converters.docx import get_paragraphs
from parser.models import all_sections
import parser.models as models
from parser.constants import show_more
from .fields import FieldsExtractor
from parser.config import logger, LanguageException


class ResumeETL:
    def __init__(self, file: typing.IO[bytes]):
        self.raw_paragraphs = get_paragraphs(file)
        self.template_lang, self.doc_lang = self.detect_language()
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
            [p.replace("\xa0", " ") for p in self.raw_paragraphs if not any(re.match(str(s), p) for s in sections)]
        )
        doc_lang = None
        for _l in detect_langs(content):
            if _l.lang == "ru" or _l.lang == "en":
                doc_lang = _l.lang
                break
        if not doc_lang:
            raise LanguageException
        return template_lang, doc_lang

    def fetch_sections(self, lang: str) -> dict:
        """
        Returns sections presented in current resume
        """
        sections_re = {k: v.re(lang) for k, v in all_sections.items()}
        return {
            k: {"title": v, "raw": []}
            for k, v in sections_re.items()
            if any(re.search(fr"{v}", par, re.IGNORECASE) for par in self.raw_paragraphs)
        }

    def populate_sections_raw(self):
        """
        Populates resume's sections with raw content
        """
        d_keys = [*self.sections.keys(), "general"]
        p_iter = iter(self.raw_paragraphs)
        p = next(p_iter)
        for l_sec, r_sec in zip(d_keys, d_keys[1:]):
            while not re.search(self.sections[r_sec]["title"], p, re.IGNORECASE):
                try:
                    if not show_more[self.template_lang] in p:
                        self.sections[l_sec]["raw"].append(p.replace("\xa0", " "))
                    p = next(p_iter)
                except StopIteration:
                    break

    def get_general(self, raw: list) -> models.General:
        if "на сайте" in raw[0]:
            raw.pop(0)
        if self.fields.extract("gender", raw[0]):
            name = None
        else:
            name = raw.pop(0)
        raw_str = " ".join(raw)
        section = models.General(
            name=name,
            gender=self.fields.extract("gender", raw_str),
            age=self.fields.extract("age", raw_str),
            birthday=self.fields.extract("birthday", raw_str),
        )
        return section

    def get_contacts(self, raw: list) -> models.Contacts:
        section = models.Contacts(
            emails=[i for p in raw if (i := self.fields.extract("email", p))],
            phones=[i for p in raw if (i := self.fields.extract("phone", p))],
            links=[i for p in raw if (i := self.fields.extract("link", p))],
            other=raw[-1],
        )
        return section

    def get_position(self, raw: list) -> models.Position:
        section = models.Position(
            updated=self.fields.extract("updated", raw.pop(0)),
            name=raw.pop(0),
            salary=raw.pop(0),
            other="\n".join(raw),
        )
        return section

    def get_experience(self, raw: list) -> models.Experience:
        section = models.Experience(
            total=self.fields.extract("experience.total", raw.pop(0)),
            items=self.fields.extract("experience.items", raw),
        )
        return section

    @staticmethod
    def get_skills(raw: list) -> models.Skills:
        section = models.Skills(items=raw[1:])
        return section

    def get_driving(self, raw: list) -> models.Driving:
        section = models.Driving(
            own_car=self.fields.extract("own_car", raw[1:]),
            categories=self.fields.extract("driving_categories", raw[1:]),
        )
        return section

    @staticmethod
    def get_about(raw: list) -> models.About:
        section = models.About(text="\n".join(raw[1:]))
        return section

    @staticmethod
    def get_recommendations(raw: list) -> models.Recommendations:
        return models.Recommendations(items=raw[1:])

    @staticmethod
    def get_portfolio(raw: list):
        pass

    def get_education(self, raw: list) -> models.Education:
        section = models.Education(
            degree=self.fields.extract("degree", raw.pop(0)), items=self.fields.extract("education.items", raw)
        )
        return section

    def get_languages(self, raw: list) -> models.Languages:
        section = models.Languages(items=self.fields.extract("languages.items", raw[1:]))
        return section

    @staticmethod
    def get_tests(raw: list) -> models.Tests:
        section = models.Tests(other="\n".join(raw[1:]))
        return section

    @staticmethod
    def get_certificates(raw: list) -> models.Certificates:
        section = models.Certificates(other="\n".join(raw[1:]))
        return section

    def get_additional_edu(self, raw: list) -> models.AdditionalEducation:
        section = models.AdditionalEducation(items=self.fields.extract("additional_edu.items", raw[1:]))
        return section

    def get_citizenship(self, raw: list) -> models.Citizenship:
        section = models.Citizenship(**self.fields.extract("citizenship", raw[1:]))
        return section

    def get_section(self, attr_name: str, data: list):
        try:
            getter = getattr(self, f"get_{attr_name}")
            return getter(data)
        except AttributeError:
            logger.error(f"No getter method for <{attr_name}> attribute found")

    def process(self) -> dict:
        resume = defaultdict()
        for name, content in self.sections.items():
            raw = content.get("raw")
            if section := self.get_section(name, raw):
                resume[name] = section.dict()
        return resume
