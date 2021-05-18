import re
import typing

from parser.config import logger


months = [
    {"name": {"ru": ["январь", "января"], "en": ["january"]}, "value": 1},
    {"name": {"ru": ["февраль", "февраля"], "en": ["february"]}, "value": 2},
    {"name": {"ru": ["март", "марта"], "en": ["march"]}, "value": 3},
    {"name": {"ru": ["апрель", "апреля"], "en": ["april"]}, "value": 4},
    {"name": {"ru": ["май", "мая"], "en": ["may"]}, "value": 5},
    {"name": {"ru": ["июнь", "июня"], "en": ["june"]}, "value": 6},
    {"name": {"ru": ["июль", "июля"], "en": ["july"]}, "value": 7},
    {"name": {"ru": ["август", "августа"], "en": ["august"]}, "value": 8},
    {"name": {"ru": ["сентябрь", "сентября"], "en": ["september"]}, "value": 9},
    {"name": {"ru": ["октябрь", "октября"], "en": ["october"]}, "value": 10},
    {"name": {"ru": ["ноябрь", "ноября"], "en": ["november"]}, "value": 11},
    {"name": {"ru": ["декабрь", "декабря"], "en": ["december"]}, "value": 12},
]

genders = {"ru": ["Мужчина", "Женщина"], "en": ["Male", "Female"]}
years_old = {"ru": ["год", "лет"], "en": ["years old"]}
born_on = {"ru": ["родился", "родилась"], "en": ["born on"]}


class FieldsExtractor:
    def __init__(self, template_lang, doc_lang):
        self.template_lang = template_lang
        self.doc_lang = doc_lang

    def extract_gender(self, text: str):
        for g in genders[self.template_lang]:
            if res := re.search(g, text):
                return res.group()
        return

    def extract_age(self, text: str) -> typing.Optional[int]:
        for y in years_old[self.template_lang]:
            if res := re.search(fr"(\d+).+{y}", text):
                return int(res.group(1))
        return

    def extract_birthday(self, text: str):
        """
        Date formats: dd.mm.yyyy / dd.mm
        """
        birthday = ""
        for b in born_on[self.template_lang]:
            if res := re.search(fr"{b}(.*)", text):
                res_str = res.group(1)
                if day := re.search(r"\d{1,2}", res_str):
                    birthday += day.group()
                if month := re.search(r"[a-zA-Zа-яА-Я]+", res_str):
                    month = month.group()
                    for _month in months:
                        if any(m in month for m in _month["name"][self.template_lang]):
                            birthday += f".{_month['value']:02d}"
                if year := re.search(r"\d{4}", res_str):
                    birthday += f".{year.group()}"
        return birthday

    @staticmethod
    def extract_email(text: str) -> typing.Optional[str]:
        if email := re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text):
            return email[0]
        return

    @staticmethod
    def extract_phone(text: str) -> typing.Optional[str]:
        if phone := re.findall(r"\+?\d{1,3}\s?\s?\(?\d{3}\)?\s?\d{3}[\s.-]\d{2}[\s.-]\d{2}", text):
            return phone[0]
        return

    @staticmethod
    def extract_link(text: str) -> typing.Optional[str]:
        if link := re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text):
            return link[0]
        return

    def extract(self, field_name: str, text: str):
        try:
            getter = getattr(self, f"extract_{field_name}")
            return getter(text)
        except AttributeError:
            logger.error(f"No extract_ method for <{field_name}> field found")
