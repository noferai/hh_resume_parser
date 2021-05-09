import re
import logging

from scraper.extractors.docx import get_paragraphs
from scraper.models import all_sections

logger = logging.getLogger(__name__)


class ResumeParser:
    # RU only
    # TODO: RU/EN detection & switch
    template_lang = "ru"
    doc_lang = "ru"

    def __init__(self, file_path: str):
        self.raw_paragraphs = get_paragraphs(file_path)
        self.sections = self.fetch_sections()
        self.populate_sections()

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

    def populate_sections(self):
        """
        Populates resume's sections with content
        """

        d_keys = [*self.sections.keys(), "contacts"]
        p_iter = iter(self.raw_paragraphs)
        for l_sec, r_sec in zip(d_keys, d_keys[1:]):
            try:
                while not re.match(self.sections[r_sec]["title"], (p := next(p_iter))):
                    self.sections[l_sec]["raw"].append(p)
            except StopIteration:
                break
