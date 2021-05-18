import re

from parser.converters.docx import get_paragraphs
from parser.models import all_sections
import parser.models as models
from parser.config import logger
from .fields import FieldsExtractor


class ResumeETL:
    # RU only
    # TODO: RU/EN detection & switch
    template_lang = "ru"
    doc_lang = "ru"

    def __init__(self, file_path: str):
        self.raw_paragraphs = get_paragraphs(file_path)
        self.sections = self.fetch_sections()
        self.populate_sections_raw()
        self.fields = FieldsExtractor(self.template_lang, self.doc_lang)

    def fetch_sections(self) -> dict:
        """
        Returns sections presented in current resume
        """
        sections_re = {k: v.re(self.template_lang) for k, v in all_sections.items()}
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
                    self.sections[l_sec]["raw"].append(p)
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
        pass

    def get_position(self, raw: list) -> models.Position:
        pass

    def get_experience(self, raw: list) -> models.Experience:
        pass

    def get_skills(self, raw: list) -> models.Skills:
        pass

    def get_about(self, raw: list) -> models.About:
        pass

    def get_recommendation(self, raw: list) -> models.Recommendation:
        pass

    def get_education(self, raw: list) -> models.Education:
        pass

    def get_languages(self, raw: list) -> models.Languages:
        pass

    def get_citizenship(self, raw: list) -> models.Citizenship:
        pass

    def get_section(self, attr_name: str, data: list):
        try:
            getter = getattr(self, f"get_{attr_name}")
            return getter(data)
        except AttributeError:
            logger.error(f"No getter method for <{attr_name}> attribute found")

    def process(self):
        for name, content in self.sections.items():
            raw = content.get("raw")
            if section := self.get_section(name, raw):
                logger.info(section.dict())
