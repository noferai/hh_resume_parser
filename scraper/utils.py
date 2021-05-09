import re


months = [
    {"ru": "Январь", "en": "January"},
    {"ru": "Февраль", "en": "February"},
    {"ru": "Март", "en": "March"},
    {"ru": "Апрель", "en": "April"},
    {"ru": "Май", "en": "May"},
    {"ru": "Июнь", "en": "June"},
    {"ru": "Июль", "en": "July"},
    {"ru": "Август", "en": "August"},
    {"ru": "Сентябрь", "en": "September"},
    {"ru": "Октябрь", "en": "October"},
    {"ru": "Ноябрь", "en": "November"},
    {"ru": "Декабрь", "en": "December"},
]


def has_cyrillic(text):
    return bool(re.search("[а-яА-Я]", text))
