import re
import typing

from collections import defaultdict
from langdetect import detect, DetectorFactory
from parser.converters.docx import get_paragraphs
from parser.models import all_sections
import parser.models as models
from parser.constants import show_more
from .fields import FieldsExtractor
from parser.config import logger, LanguageException


class ResumeETL:
    def __init__(self, file_path: str):
        self.raw_paragraphs = get_paragraphs(file_path)
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
        if (doc_lang := detect(content)) not in ("ru", "en"):
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
            if any(re.match(str(v), par) for par in self.raw_paragraphs)
        }

    def populate_sections_raw(self):
        """
        Populates resume's sections with raw content
        """
        d_keys = [*self.sections.keys(), "contacts"]
        p_iter = iter(self.raw_paragraphs)
        p = next(p_iter)
        for l_sec, r_sec in zip(d_keys, d_keys[1:]):
            while not re.match(self.sections[r_sec]["title"], p):
                try:
                    if not show_more[self.template_lang] in p:
                        self.sections[l_sec]["raw"].append(p.replace("\xa0", " "))
                    p = next(p_iter)
                except StopIteration:
                    break

    def get_general(self, raw: list) -> models.General:
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

    @staticmethod
    def get_about(raw: list) -> models.About:
        section = models.About(text="\n".join(raw[1:]))
        return section

    def get_recommendations(self, raw: list) -> models.Recommendations:
        section = models.Recommendations(items=self.fields.extract("recommendations.items", raw[1:]))
        return section

    def get_education(self, raw: list) -> models.Education:
        section = models.Education(
            degree=self.fields.extract("degree", raw.pop(0)), items=self.fields.extract("education.items", raw)
        )
        return section

    def get_languages(self, raw: list) -> models.Languages:
        section = models.Languages(items=self.fields.extract("languages.items", raw[1:]))
        return section

    @staticmethod
    def get_citizenship(raw: list) -> models.Citizenship:
        section = models.Citizenship(
            citizenship=raw[1].split(": ")[1], permission=raw[2].split(": ")[1], commute=raw[3].split(": ")[1]
        )
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
