import re
import collections
import logging
import yaml

from .docx import get_paragraphs

logger = logging.getLogger(__name__)


class ResumeParser:
    # TODO: RU/EN detection & switch

    def __init__(self, file_path: str):
        self.paragraphs = get_paragraphs(file_path)

    def get_sections(self) -> collections.OrderedDict:
        """
        Returns sections for current resume
        """
        with open("parser/static/resume_sections.yml", "r") as f:
            sections = yaml.safe_load(f)

        filtered_sections = collections.OrderedDict(
            {
                s_title: s_attrs
                for s_title, s_attrs in sections.items()
                if any(re.match(s_attrs["re"]["ru"], par) for par in self.paragraphs)
            }
        )
        return filtered_sections

    def get_content(self):
        sections = self.get_sections()

        d_keys = list([*sections.keys(), list(sections.keys())[1]])
        idx = 0
        for l_sec, r_sec in zip(d_keys, d_keys[1:]):
            while idx < len(self.paragraphs):
                if not re.match(sections[r_sec]["re"]["ru"], self.paragraphs[idx]):
                    sections[l_sec]["content"].append(self.paragraphs[idx])
                    idx += 1
                else:
                    break
        return sections
