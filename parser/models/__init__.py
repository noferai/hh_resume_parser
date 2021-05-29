from .resume import (
    General,
    Contacts,
    Position,
    Experience,
    Skills,
    About,
    Recommendations,
    Education,
    Languages,
    Citizenship,
)
from .resume import Resume


all_sections = {
    section: getattr(Resume, section)
    for section in [
        "general",
        "contacts",
        "position",
        "experience",
        "skills",
        "about",
        "recommendations",
        "portfolio",
        "education",
        "languages",
        "citizenship",
    ]
}
