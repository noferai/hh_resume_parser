import re
import logging

from scraper.extractors.docx import get_paragraphs
from scraper.models import Resume, all_sections

logger = logging.getLogger(__name__)


class ResumeParser:
    # RU only
    # TODO: RU/EN detection & switch
    template_lang = "ru"
    doc_lang = "ru"

    def __init__(self, file_path: str):
        self.raw_paragraphs = get_paragraphs(file_path)
        self.sections = self.get_sections

    def get_sections(self):
        sections_re = {section: getattr(Resume, section).re(self.template_lang) for section in all_sections.keys()}
        return {
            section: re_
            for section, re_ in sections_re.items()
            if any(re.match(str(re_), par) for par in self.raw_paragraphs)
        }

    # def get_sections_(self) -> dict:
    #     """
    #     Returns resume divided into sections
    #     """
    #
    #     d_keys = list([*self.sections.keys(), list(self.sections.keys())[1]])
    #     idx = 0
    #     for l_sec, r_sec in zip(d_keys, d_keys[1:]):
    #         while idx < len(self.raw_paragraphs):
    #             if re_search := self.sections_re[r_sec]["re"]:
    #                 if not re.match(re_search, self.sections_re[idx]):
    #                     sections[l_sec]["raw"].append(self.raw_paragraphs[idx])
    #                     idx += 1
    #                 else:
    #                     break
    #
    #     return {key: {"title": value["raw"][0], "raw": value["raw"][1:]} for key, value in sections.items()}

    def get_name(self):
        pass

    def process(self):
        pass
