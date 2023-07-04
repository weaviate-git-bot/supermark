from typing import Optional, List

from pydantic import BaseModel


class ExtensionDocument(BaseModel):
    raw_text: str
    url: str
    title: str
    image_urls: list
    timestamp: int
    folder: str


class UrlMetadataInfo(BaseModel):
    is_bookmarked: bool
    folders: List[str]

class ExtensionPDFDocument(BaseModel):
    pdf_bytes: list
    url: str
    title: str
    timestamp: int
    folder: str