import re
import typing
from datetime import datetime

from funcy.seqs import chunks

from parser.models import Experience, Recommendations, Education, Languages
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
years_months = {"ru": ["год", "лет", "месяц"], "en": ["year", "month"]}
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
        for y in years_months[self.template_lang]:
            if res := re.search(fr"(\d+)\s+{y}", text):
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

    @staticmethod
    def extract_updated(text: str) -> typing.Optional[datetime]:
        if match := re.search(r"(\d{2}\.\d{2}\.\d{4})\s\d{2}:\d{2}", text):
            try:
                d_t = datetime.strptime(match.group(), "%d.%m.%Y %H:%M")
                return d_t
            except ValueError:
                return

    def extract_experience_total(self, text: str) -> typing.Optional[str]:
        if match := re.search(fr"\d+\s+({'|'.join(years_months[self.template_lang])}).+", text):
            return match.group()
        return

    @staticmethod
    def extract_experience_items(text: list) -> list:
        items = []
        for duration, total, company, company_info, _, position, other in chunks(7, text):
            items.append(
                Experience.Item(
                    duration=duration,
                    total=total,
                    company=company,
                    company_info=company_info,
                    position=position,
                    other=other,
                )
            )
        return items

    @staticmethod
    def extract_recommendations_items(text: list) -> list:
        items = [Recommendations.Item(org=org, person=person) for org, person in chunks(2, text)]
        return items

    @staticmethod
    def extract_degree(text: str) -> typing.Optional[str]:
        if match := re.search(r"\((.*)\)", text):
            return match.group(1)
        return text

    @staticmethod
    def extract_education_items(text: list) -> list:
        items = [Education.Item(year=year, name=name, other=other) for year, name, other in chunks(3, text)]
        return items

    @staticmethod
    def extract_languages_items(text: list) -> list:
        items = [
            Languages.Item(name=lang_i[0], lvl=", ".join(lang_i[1:])) for item in text if (lang_i := item.split(" — "))
        ]
        return items

    def extract(self, field_name: str, text: typing.Union[str, list]):
        try:
            getter = getattr(self, f"extract_{field_name.replace('.', '_')}")
            return getter(text)
        except AttributeError:
            logger.error(f"No extract_ method for <{field_name}> field found")
