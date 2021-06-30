from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, AnyUrl, Field, validator


class Title(BaseModel):
    searchable: bool = True
    exact: bool = True
    ru: str = ""
    en: str = ""


class Section(BaseModel):
    title: Title
    other: Optional[str]

    @classmethod
    def re(cls, lang: str) -> Optional[str]:
        d_title = cls.__fields__["title"].default.dict()
        if d_title["searchable"]:
            return f"^{d_title[lang]}$" if d_title["exact"] else d_title[lang]
        return None


class General(Section):
    title = Title(exact=False)
    name: Optional[str]
    gender: Optional[str]
    birthday: Optional[str]
    age: Optional[int]

    @validator("name")
    def is_alphabetic(cls, v: str):
        if v is not None:
            assert not any(c.isdigit() for c in v), "Must be alphabetic"
        return v


class Contacts(Section):
    title = Title(ru="Контакты", en="Контакты")
    phones: List[Optional[str]]
    emails: List[Optional[EmailStr]]
    links: List[Optional[AnyUrl]]
    location: Optional[str]


class Position(Section):
    title = Title(ru="Резюме обновлено", en="Resume updated", exact=False)
    name: str
    salary: Optional[str]
    updated: datetime


class Experience(Section):
    class Item(BaseModel):
        duration: str
        total: str
        company: str
        company_info: Optional[str]
        position: str
        other: str

    title = Title(ru="Опыт работы", en="Work experience", exact=False)
    total: str
    items: List[Item]


class Skills(Section):
    title = Title(ru="Ключевые навыки", en="Key skills")
    items: List[str]


class Driving(Section):
    title = Title(ru="Опыт вождения", en="Driving experience")
    own_car: bool
    categories: List[str]


class About(Section):
    title = Title(ru="Обо мне", en="About me")
    text: str


class Recommendations(Section):
    title = Title(ru="Рекомендации", en="Recommendations")
    items: List[str]


class Portfolio(Section):
    title = Title(ru="Портфолио", en="Portfolio")


class Education(Section):
    class Item(BaseModel):
        year: int
        name: str = Field(..., min_length=1)
        other: Optional[str]

    title = Title(ru="Образование", en="Education", exact=False)
    degree: Optional[str]
    items: List[Item]


class AdditionalEducation(Section):
    class Item(BaseModel):
        year: int
        name: str = Field(..., min_length=1)
        other: Optional[str]

    title = Title(ru="Повышение квалификации, курсы", en="Professional development, courses")
    items: List[Item]


class Languages(Section):
    class Item(BaseModel):
        name: str = Field(..., min_length=1)
        lvl: str = Field(..., min_length=1)

    title = Title(ru="Знание языков", en="Languages")
    items: List[Item]


class Tests(Section):
    title = Title(ru="Тесты, экзамены", en="Tests, examinations")


class Certificates(Section):
    title = Title(ru="Электронные сертификаты", en="Electronic Certificates")


class Citizenship(Section):
    title = Title(ru="Гражданство, время в пути до работы", en="Citizenship, travel time to work")
    citizenship: Optional[str]
    permission: Optional[str]
    commute: Optional[str]


class Resume(BaseModel):
    general = General
    contacts = Contacts
    position = Position
    experience = Experience
    skills = Skills
    driving = Driving
    about = About
    recommendations = Recommendations
    portfolio = Portfolio
    education = Education
    languages = Languages
    additional_edu = AdditionalEducation
    tests = Tests
    certificates = Certificates
    citizenship = Citizenship
