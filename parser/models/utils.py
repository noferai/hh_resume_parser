from funcy import with_next


def fix_paragraph(paragraph: list):
    """Fixes <highlighted> words in paragraph"""
    paragraph = paragraph.copy()
    while True:
        new_paragraph = []
        skip = False
        for w, next_w in with_next(paragraph, fill=""):
            if skip:
                skip = False
                continue
            if w.endswith(" "):
                new_paragraph.append(f"{w}{next_w}")
                skip = True
            elif next_w.startswith(" ") or next_w.startswith(","):
                new_paragraph.append(f"{w}{next_w}")
                skip = True
            else:
                new_paragraph.append(w)
        if paragraph != new_paragraph:
            paragraph = new_paragraph.copy()
        else:
            break

    return paragraph[0] if len(paragraph) == 1 else paragraph
