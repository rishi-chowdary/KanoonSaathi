from pydantic import BaseModel, Field


class PageExtraction(BaseModel):
    page_number: int
    text: str
    ocr_used: bool = False


class SectionExtraction(BaseModel):
    title: str
    section_ref: str
    page_number: int


class ChunkExtraction(BaseModel):
    chunk_index: int
    page_start: int
    page_end: int
    section_ref: str | None = None
    content: str
    token_count: int


class ExtractionResponse(BaseModel):
    pages: list[PageExtraction] = Field(default_factory=list)
    sections: list[SectionExtraction] = Field(default_factory=list)
    chunks: list[ChunkExtraction] = Field(default_factory=list)
    language_guess: str = "en"
    warnings: list[str] = Field(default_factory=list)


class ExtractionErrorResponse(BaseModel):
    code: str
    detail: str
