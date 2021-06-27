import zipfile
import typing

from lxml import etree

# MS Word prefixes / namespace matches used in document.xml
ns_prefixes = {
    "mo": "{http://schemas.microsoft.com/office/mac/office/2008/main}",
    "o": "{urn:schemas-microsoft-com:office:office}",
    "ve": "{http://schemas.openxmlformats.org/markup-compatibility/2006}",
    # Text Content
    "w": "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}",
    "w10": "{urn:schemas-microsoft-com:office:word}",
    "wne": "{http://schemas.microsoft.com/office/word/2006/wordml}",
    # Properties (core and extended)
    "cp": "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}",
    "dc": "{http://purl.org/dc/elements/1.1/}",
    "ep": "{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}",
    "xsi": "{http://www.w3.org/2001/XMLSchema-instance}",
    # Content Types
    "ct": "{http://schemas.openxmlformats.org/package/2006/content-types}",
    # Package Relationships
    "r": "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}",
    "pr": "{http://schemas.openxmlformats.org/package/2006/relationships}",
}


def get_xml(file: typing.IO[bytes]):
    """
    Returns raw MS Word xml
    """
    with zipfile.ZipFile(file) as doc:
        xml_content = doc.read("word/document.xml")
    document = etree.fromstring(xml_content)
    return document


def get_paragraphs(file: typing.IO[bytes]) -> list:
    """
    Returns the raw text of a document as a list of paragraphs
    """
    doc_xml = get_xml(file)
    paragraphs = [element for element in doc_xml.iter() if element.tag == f"{ns_prefixes['w']}p"]
    text = []

    for paragraph in paragraphs:
        p_text = ""
        for element in paragraph.iter():
            if element.tag == f"{ns_prefixes['w']}t":
                if element.text:
                    p_text += element.text
            elif element.tag == f"{ns_prefixes['w']}tab":
                p_text += "\t"
        if len(p_text) > 0:
            text.append(p_text)
    return text
