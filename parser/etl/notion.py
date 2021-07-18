import copy
from collections import defaultdict
from config import logger


class NotionConverter:
    def __init__(self, sections: dict):
        sections = copy.deepcopy(sections)
        _general = sections.pop("general")
        _contacts = sections.pop("contacts") if "contacts" in sections else defaultdict(lambda: "")
        _position = sections.pop("position") if "position" in sections else defaultdict(lambda: "")
        self.personal = {
            "name": _general["name"] if _general["name"] else "Не указано",
            "birthday": _general["birthday"] if _general["birthday"] else "Не указано",
            "contacts": ", ".join([*_contacts["phones"], *_contacts["emails"], *_contacts["links"]]),
            "location": _contacts["location"] if _contacts["location"] else "Не указано",
            "position": f"_{p}" if (p := sections.get("name")) else "",
        }
        self.sections = sections

    @staticmethod
    def text_wrapper(_text: str, **kwargs) -> dict:
        annotations = {"annotations": kwargs} if kwargs else {}
        return {
            "type": "text",
            "text": {"content": _text},
            **annotations,
        }

    @staticmethod
    def block_wrapper(_type: str, *content) -> dict:
        return {
            "object": "block",
            "type": _type,
            _type: {"text": content},
        }

    def get_title(self):
        return {
            "title": {
                "title": [{"type": "text", "text": {"content": f"{self.personal['name']} {self.personal['position']}"}}]
            }
        }

    def get_general(self) -> list:
        return [
            self.block_wrapper("heading_2", self.text_wrapper("Личные данные")),
            self.block_wrapper(
                "paragraph",
                self.text_wrapper("Дата рождения: ", bold=True),
                self.text_wrapper(self.personal["birthday"]),
            ),
            self.block_wrapper(
                "paragraph",
                self.text_wrapper("Место нахождения: ", bold=True),
                self.text_wrapper(self.personal["location"]),
            ),
            self.block_wrapper(
                "paragraph",
                self.text_wrapper("Контакты: ", bold=True),
                self.text_wrapper(self.personal["contacts"]),
            ),
        ]

    def convert_experience(self, section: dict) -> list:
        def convert_items() -> list:
            items = []
            for item in section["items"]:
                other = (
                    [self.block_wrapper("paragraph", self.text_wrapper(i)) for i in item["other"]]
                    if isinstance(item["other"], list)
                    else [self.block_wrapper("paragraph", self.text_wrapper(item["other"]))]
                )
                items.extend(
                    [
                        self.block_wrapper(
                            "heading_3",
                            self.text_wrapper(
                                f"{item['duration']} - {item['company']}{', %s'%item['company_info'] if item['company_info'] else ''}",
                                bold=True,
                                color="gray_background",
                            ),
                        ),
                        self.block_wrapper("paragraph", self.text_wrapper(item["position"], bold=True)),
                        *other,
                    ]
                )
            return items

        return [
            self.block_wrapper("paragraph", self.text_wrapper(f"Общий стаж {section['total']}", bold=True)),
            *convert_items(),
        ]

    def convert_skills(self, section: dict) -> list:
        return [self.block_wrapper("bulleted_list_item", self.text_wrapper(item)) for item in section["items"]]

    def convert_driving(self, section: dict) -> list:
        return [
            self.block_wrapper(
                "paragraph", self.text_wrapper(f"Свой автомобиль: {'Да' if section['own_car'] else 'Нет'}")
            ),
            self.block_wrapper("paragraph", self.text_wrapper(f"Категории: {', '.join(section['categories'])}")),
        ]

    def convert_about(self, section: dict) -> list:
        if isinstance(section["text"], list):
            return [self.block_wrapper("paragraph", self.text_wrapper(p)) for p in section["text"]]
        return [self.block_wrapper("paragraph", self.text_wrapper(section["text"]))]

    def convert_recommendations(self, section: dict) -> list:
        return self.convert_skills(section)

    def convert_education(self, section: dict) -> list:
        items = []
        for item in section["items"]:
            items.extend(
                [
                    self.block_wrapper("heading_3", self.text_wrapper(f"{item['name']} - {item['year']}", bold=True)),
                    self.block_wrapper("paragraph", self.text_wrapper(item["other"])),
                ]
            )
        return items

    def convert_languages(self, section: dict) -> list:
        return [
            self.block_wrapper("bulleted_list_item", self.text_wrapper(f"{item['name']}: {item['lvl']}"))
            for item in section["items"]
        ]

    def convert_additional_edu(self, section: dict) -> list:
        return [
            self.block_wrapper(
                "bulleted_list_item",
                self.text_wrapper(f"{item['name']} - {item['year']}. ", bold=True),
                self.text_wrapper(item["other"]),
            )
            for item in section["items"]
        ]

    def convert_tests(self, section: dict) -> list:
        return self.convert_additional_edu(section)

    def convert_citizenship(self, section: dict) -> list:
        return [
            self.block_wrapper("paragraph", self.text_wrapper(f"Гражданство: {section['citizenship']}")),
            self.block_wrapper("paragraph", self.text_wrapper(f"Разрешение на работу: {section['permission']}")),
            self.block_wrapper(
                "paragraph", self.text_wrapper(f"Желательное время в пути до работы: {section['commute']}")
            ),
        ]

    def convert_section(self, attr_name: str, data: dict) -> list:
        try:
            converter = getattr(self, f"convert_{attr_name}")
            section_title = self.block_wrapper("heading_1", self.text_wrapper(data.pop("title")["ru"]))
            section_content = converter(data)
            return [section_title, *section_content]
        except AttributeError:
            pass

    def convert_resume(self) -> dict:
        """Returns resume as Notion page"""
        resume = self.get_general()
        for name, content in self.sections.items():
            if section := self.convert_section(name, content):
                resume.extend(section)
        return {"properties": self.get_title(), "children": resume}