import re
from datetime import datetime
from typing import Union, Optional

import funcy as fc

from config import logger
from parser.constants import months, genders, years_months, born_on, citizenship, own_car, willing
from parser.models import Experience, Education, Languages, AdditionalEducation


def join_text(func):
    """If a list of strings passed, converts it to one string"""

    def wrapper(self, text):
        return func(self, fc.str_join(text))

    return wrapper


class FieldsExtractor:
    def __init__(self, template_lang, doc_lang):
        self.template_lang = template_lang
        self.doc_lang = doc_lang

    @join_text
    def extract_gender(self, text: str) -> Optional[str]:
        for gender in genders[self.template_lang]:
            if res := re.search(gender, text):
                return res.group()
        return

    @join_text
    def extract_age(self, text: str) -> Optional[int]:
        for y in years_months[self.template_lang]:
            if res := re.search(fr"(\d+)\s+{y}", text):
                return int(res.group(1))
        return

    @join_text
    def extract_birthday(self, text: str):
        """
        Possible date formats: dd.mm.yyyy / dd.mm
        """
        birthday = ""
        for b in born_on[self.template_lang]:
            if res := re.search(fr"{b}(.*)", text):
                res_str = res.group(1)
                if day := re.search(r"\d{1,2}", res_str):
                    birthday += f"{int(day.group()):02d}"
                if month := re.search(r"[a-zA-Zа-яА-Я]+", res_str):
                    month = month.group()
                    for _month in months:
                        if any(m in month for m in _month["name"][self.template_lang]):
                            birthday += f".{_month['value']:02d}"
                if year := re.search(r"\d{4}", res_str):
                    birthday += f".{year.group()}"
        return birthday if len(birthday) > 0 else None

    @join_text
    def extract_email(self, text: str) -> Optional[str]:
        if email := re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text):
            return email[0]
        return

    @join_text
    def extract_phone(self, text: str) -> Optional[str]:
        if phone := re.findall(r"\+?\d{1,3}\s?\(?\d{3}\)?\s?\d{2,3}[\s.-]\d{2,3}[\s.-]\d{2,3}", text):
            return phone[0]
        return

    @join_text
    def extract_link(self, text: str) -> Optional[str]:
        if link := re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text):
            return link[0]
        return

    @join_text
    def extract_location(self, text: str) -> Optional[str]:
        location = []
        for word in text.split(","):
            if willing[self.template_lang] in word:
                return ", ".join(location)
            location.append(word)

    @join_text
    def extract_updated(self, text: str) -> Optional[datetime]:
        if match := re.search(r"(\d{2}\.\d{2}\.\d{4})\s\d{2}:\d{2}", text):
            try:
                d_t = datetime.strptime(match.group(), "%d.%m.%Y %H:%M")
                return d_t
            except ValueError:
                return

    @join_text
    def extract_salary(self, text: str) -> Optional[str]:
        if len(re.findall(r"\d", text)) > 3:
            return text

    @join_text
    def extract_experience_total(self, text: str) -> Optional[str]:
        if match := re.search(fr"\d+.+({'|'.join(years_months[self.template_lang])}).*", text, re.IGNORECASE):
            return match.group()
        return

    def extract_experience_items(self, text: list) -> list:
        _months = [m for _month in months for m in _month["name"][self.template_lang]]
        indices = [
            *[i for i, p in enumerate(text) if (_p := fc.str_join(p).lower()) and any(m in _p for m in _months)],
            len(text),
        ]  # Experience item always starts with duration containing months
        fields = ["duration", "total", "company", "company_info", "position", "other"]
        fields_w = ["duration", "total", "company", "position", "other"]

        items = []
        for i, next_ in fc.with_next(indices, fill=0):
            if next_ - i == len(fields):
                items.append(Experience.Item(**dict(zip(fields, text[i:next_]))))
            elif next_ - i == len(fields_w):
                items.append(Experience.Item(**dict(zip(fields_w, text[i:next_]))))
        return items

    def extract_own_car(self, text: list) -> bool:
        return any(s == own_car["has"][self.template_lang] for s in text)

    def extract_driving_categories(self, text: list) -> list:
        categories = []
        for s in text:
            if s != own_car["has"][self.template_lang]:
                categories = [w.replace(",", "") for w in s.split() if len(w) <= 3]
        return categories

    @staticmethod
    def extract_education_items(text: list) -> list:
        indices = [i for i, x in enumerate(text) if fc.str_join(x).isdigit()]
        fields = list(Education.Item.__fields__.keys())
        items = [Education.Item(**dict(zip(fields, text[i:next_]))) for i, next_ in fc.with_next(indices)]
        return items

    @staticmethod
    def extract_additional_edu_items(text: list) -> list:
        indices = [i for i, x in enumerate(text) if fc.str_join(x).isdigit()]
        fields = list(AdditionalEducation.Item.__fields__.keys())
        items = [AdditionalEducation.Item(**dict(zip(fields, text[i:next_]))) for i, next_ in fc.with_next(indices)]
        return items

    @staticmethod
    def extract_languages_items(text: list) -> list:
        items = [
            Languages.Item(name=lang_i[0], lvl=", ".join(lang_i[1:])) for item in text if (lang_i := item.split(" — "))
        ]
        return items

    @join_text
    def extract_degree(self, text: str) -> Optional[str]:
        if match := re.search(r"\((.*)\)", text):
            return match.group(1)
        return text

    def extract_citizenship(self, text: list) -> dict:
        result = {}
        for p in text:
            _p = fc.str_join(p)
            for k, v in citizenship.items():
                if re.search(v[self.template_lang], _p, re.IGNORECASE):
                    result[k] = _p.split(": ")[1]
        return result

    def extract(self, field_name: str, text: Union[str, list]):
        try:
            getter = getattr(self, f"extract_{field_name.replace('.', '_')}")
            return getter(text)
        except AttributeError:
            logger.error(f"No extract_ method for <{field_name}> field found")
