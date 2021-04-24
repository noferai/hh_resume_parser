import re


def has_cyrillic(text):
    return bool(re.search("[а-яА-Я]", text))
