from .resume import (
    General,
    Contacts,
    Position,
    Experience,
    Skills,
    Driving,
    About,
    Recommendations,
    Portfolio,
    Education,
    Languages,
    AdditionalEducation,
    Tests,
    Certificates,
    Citizenship,
)
from .resume import Resume


all_sections = {
    section: getattr(Resume, section)
    for section in [
        "contacts",
        "position",
        "experience",
        "skills",
        "driving",
        "about",
        "recommendations",
        "portfolio",
        "education",
        "languages",
        "additional_edu",
        "tests",
        "certificates",
        "citizenship",
    ]
}
