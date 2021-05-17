import re
import logging
import typing


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


logger = logging.getLogger(__name__)


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

    # def extract_email(self, text: str) -> typing.Optional[str]:
    #     email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    #     if email:
    #         try:
    #             return email[0].split()[0].strip(";")
    #         except IndexError:
    #             return
    #
    # def extract_phone(self, text: str) -> typing.Optional[str]:
    #     pass

    def extract(self, field_name: str, text: str):
        try:
            getter = getattr(self, f"extract_{field_name}")
            getter(text)
        except AttributeError:
            logger.error(f"No extract_ method for <{field_name}> field found")
