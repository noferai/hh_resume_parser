from .resume import (
    General,
    Contacts,
    Position,
    Experience,
    Skills,
    About,
    Recommendation,
    Education,
    Languages,
    Citizenship,
)
from .resume import Resume


all_sections = {
    "general": {"model": General, "raw": []},
    "contacts": {"model": Contacts, "raw": []},
    "position": {"model": Position, "raw": []},
    "experience": {"model": Experience, "raw": []},
    "skills": {"model": Skills, "raw": []},
    "about": {"model": About, "raw": []},
    "recommendation": {"model": Recommendation, "raw": []},
    "education": {"model": Education, "raw": []},
    "languages": {"model": Languages, "raw": []},
    "citizenship": {"model": Citizenship, "raw": []},
}
