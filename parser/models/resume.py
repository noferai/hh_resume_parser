from typing import List, Optional, Union
from datetime import datetime

import funcy as fc
from pydantic import BaseModel, EmailStr, AnyUrl, Field, validator

from .utils import fix_paragraph


class Title(BaseModel):
    searchable: bool = True
    exact: bool = True
    ru: str = ""
    en: str = ""


class Section(BaseModel):
    title: Title
    min_length: int = 2
    other: Optional[Union[str, list]]

    @classmethod
    def re(cls, lang: str) -> Optional[dict]:
        d_title = cls.__fields__["title"].default.dict()
        d_length = cls.__fields__["min_length"].default
        if d_title["searchable"]:
            return {"title": f"^{d_title[lang]}$" if d_title["exact"] else d_title[lang], "min_length": d_length}
        return None


class General(Section):
    title = Title(searchable=False)
    name: Optional[Union[str, list]]
    gender: Optional[str]
    birthday: Optional[str]
    age: Optional[int]

    @validator("name")
    def is_alphabetic(cls, v: str):
        if v:
            assert not any(c.isdigit() for c in v), "Must be alphabetic"
        return v

    @validator("name", pre=True)
    def join_str(cls, v):
        if v:
            return fc.str_join(v)


class Contacts(Section):
    title = Title(ru="Контакты", en="Контакты")
    phones: List[Optional[str]]
    emails: List[Optional[EmailStr]]
    links: List[Optional[AnyUrl]]
    location: Optional[str]


class Position(Section):
    title = Title(ru="Резюме обновлено", en="Resume updated", exact=False)
    min_length = 1
    name: str
    salary: Optional[str]
    updated: datetime

    @validator("name", pre=True)
    def join_str(cls, v):
        return fc.str_join(v)


class Experience(Section):
    class Item(BaseModel):
        duration: Union[str, list]
        total: Union[str, list]
        company: Union[str, list]
        company_info: Optional[Union[str, list]]
        position: Union[str, list]
        other: Union[str, list]

        @validator("duration", "total", "company", "company_info", "position", pre=True)
        def join_str(cls, v):
            return fc.str_join(v)

        @validator("other", pre=True)
        def fix_text(cls, v):
            if isinstance(v, list):
                return fix_paragraph(v)
            return v

    title = Title(ru="Опыт работы", en="Work experience", exact=False)
    min_length = 3
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
    text: Union[str, list]

    @validator("text", pre=True)
    def fix_text(cls, v):
        if isinstance(v, list):
            return fix_paragraph(v)
        return v


class Recommendations(Section):
    title = Title(ru="Рекомендации", en="Recommendations")
    items: List[Union[str, list]]

    @validator("items", pre=True)
    def join_str(cls, v):
        return [fc.str_join(i) for i in v]


class Portfolio(Section):
    title = Title(ru="Портфолио", en="Portfolio")


class Education(Section):
    class Item(BaseModel):
        year: int
        name: str = Field(..., min_length=1)
        other: Union[str, list, None]

        @validator("year", "name", "other", pre=True)
        def join_str(cls, v):
            return fc.str_join(v)

    title = Title(ru="Образование", en="Education", exact=False)
    min_length = 4
    degree: Optional[str]
    items: List[Item]


class AdditionalEducation(Section):
    class Item(BaseModel):
        year: int
        name: str = Field(..., min_length=1)
        other: Union[str, list, None]

        @validator("year", "name", "other", pre=True)
        def join_str(cls, v):
            return fc.str_join(v)

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
