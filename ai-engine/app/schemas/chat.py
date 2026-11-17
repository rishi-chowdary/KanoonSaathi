from typing import Literal
from pydantic import BaseModel, Field


class RetrievedChunkItem(BaseModel):
    chunk_id: str | None = None
    page_number: int = Field(default=1, description="Source page number of the chunk")
    content: str = Field(description="Text content of the document chunk")
    section_ref: str | None = Field(default=None, description="Optional section reference or heading")


class ChatMessageItem(BaseModel):
    role: Literal["user", "assistant"] = Field(description="Role of the speaker")
    content: str = Field(description="Message text")


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000, description="User question about the document")
    retrieved_chunks: list[RetrievedChunkItem] = Field(
        default_factory=list, description="Top-k relevant document excerpts"
    )
    conversation_history: list[ChatMessageItem] = Field(
        default_factory=list, description="Recent conversation history"
    )


class StructuredCitation(BaseModel):
    page: int = Field(description="Page number containing the supporting evidence")
    section_ref: str | None = Field(default=None, description="Section heading or reference if stated")
    quote: str = Field(description="Verbatim excerpt from the chunk supporting the assertion")
    quote_verified: bool = Field(default=True, description="Whether the quote was verified in the chunk text")


class RawChatResult(BaseModel):
    answer: str = Field(
        description="Concise, direct answer based strictly on the provided document excerpts."
    )
    citations: list[StructuredCitation] = Field(
        default_factory=list,
        description="Structured citations with verbatim quotes and page numbers supporting the answer.",
    )
    confidence: Literal["supported", "partially supported", "not found"] = Field(
        description="Grounded confidence level of the answer relative to the excerpts."
    )


class ChatResponse(BaseModel):
    answer: str
    citations: list[StructuredCitation] = Field(default_factory=list)
    confidence: Literal["supported", "partially supported", "not found"]
    addressed_in_document: bool = Field(
        description="True if the question is supported or partially supported in the excerpts."
    )

