import typing
import zipfile

from lxml import etree

# MS Word prefixes / namespace matches used in document.xml
ns_prefixes = {
    "mo": r"{http://schemas.microsoft.com/office/mac/office/2008/main}",
    "o": r"{urn:schemas-microsoft-com:office:office}",
    "ve": r"{http://schemas.openxmlformats.org/markup-compatibility/2006}",
    # Text Content
    "w": r"{http://schemas.openxmlformats.org/wordprocessingml/2006/main}",
    "w10": r"{urn:schemas-microsoft-com:office:word}",
    "wne": r"{http://schemas.microsoft.com/office/word/2006/wordml}",
    # Properties
    "cp": r"{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}",
    "dc": r"{http://purl.org/dc/elements/1.1/}",
    "ep": r"{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}",
    "xsi": r"{http://www.w3.org/2001/XMLSchema-instance}",
    # Content Types
    "ct": r"{http://schemas.openxmlformats.org/package/2006/content-types}",
    # Package Relationships
    "r": r"{http://schemas.openxmlformats.org/officeDocument/2006/relationships}",
    "pr": r"{http://schemas.openxmlformats.org/package/2006/relationships}",
}
spec_chars = ["(", ")"]


def normalize_text(text: list, threshold: int) -> typing.Union[list, str]:
    i = 1
    while i < len(text):
        if len(text[i].split()) < threshold or len(text[i - 1].split()) < threshold:
            text[i - 1 : i + 1] = ["".join(text[i - 1 : i + 1])]
            i = 0
        i += 1

    return text[0] if len(text) == 1 else text


def get_xml(file: typing.IO[bytes]):
    """Returns raw MS Word xml"""
    with zipfile.ZipFile(file) as doc:
        xml_content = doc.read("word/document.xml")
    document = etree.fromstring(xml_content)
    return document


def get_paragraphs(file: typing.IO[bytes]) -> list:
    """Returns the raw text of a document as a list of paragraphs"""
    doc_xml = get_xml(file)
    paragraphs = [element for element in doc_xml.iter() if element.tag == f"{ns_prefixes['w']}p"]
    text = []

    for paragraph in paragraphs:
        p_line = []
        for element in paragraph.iter():
            if element.tag == f"{ns_prefixes['w']}t" and element.text:
                p_line.append(element.text.replace("\xa0", " "))
        if len(p_line) > 0:
            if len(p_line) > 1:
                text.append(p_line)
            else:
                text.extend(p_line)
    return text
