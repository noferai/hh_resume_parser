from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, AnyUrl


class Title(BaseModel):
    searchable: bool = True
    ru: str = ""
    en: str = ""


class Section(BaseModel):
    title: Title
    other: Optional[str]

    @classmethod
    def re(cls, lang: str) -> Optional[str]:
        d_title = cls.__fields__["title"].default.dict()
        if d_title["searchable"]:
            return d_title[lang]
        return None


class General(Section):
    title = Title()
    name: str
    gender: Optional[str]
    birthday: Optional[str]
    age: Optional[int]


class Contacts(Section):
    title = Title(ru="Контакты", en="Контакты")
    phones: List[Optional[str]]
    emails: List[Optional[EmailStr]]
    links: List[Optional[AnyUrl]]


class Position(Section):
    title = Title(ru="Резюме обновлено", en="Resume updated")
    name: str
    salary: Optional[str]
    updated: datetime


class Experience(Section):
    class Item(BaseModel):
        duration: str
        total: str
        company: str
        company_info: str
        position: str
        other: str

    title = Title(ru="Опыт работы", en="Work experience")
    total: str
    items: List[Item]


class Skills(Section):
    title = Title(ru="Ключевые навыки", en="Key skills")
    items: List[str]


class About(Section):
    title = Title(ru="Обо мне", en="About me")
    text: str


class Recommendations(Section):
    class Item(BaseModel):
        org: str
        person: str

    title = Title(ru="Рекомендации", en="")
    items: List[Item]


class Education(Section):
    class Item(BaseModel):
        year: str
        place: str
        other: str

    title = Title(ru="Высшее образование", en="Higher education")
    degree: Optional[str]
    items: List[Optional[Item]]


class Languages(Section):
    class Item(BaseModel):
        name: str
        lvl: str

    title = Title(ru="Знание языков", en="Languages")
    items: List[Item]


class Citizenship(Section):
    title = Title(ru="Гражданство, время в пути до работы", en="Citizenship, travel time to work")
    citizenship: str
    permission: Optional[str]


class Resume(BaseModel):
    general = General
    contacts = Contacts
    position = Position
    experience = Experience
    skills = Skills
    about = About
    recommendations = Recommendations
    education = Education
    languages = Languages
    # training:
    citizenship = Citizenship
