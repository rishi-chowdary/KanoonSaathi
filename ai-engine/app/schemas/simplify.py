from typing import Literal, Optional
from pydantic import BaseModel, Field


class GlossaryTerm(BaseModel):
    term: str = Field(..., description="The legal term or phrase being defined")
    definition: str = Field(..., description="A concise, plain-language definition of the legal term")


class SimplifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=15000, description="Arbitrary legal text to simplify")
    document_context: Optional[str] = Field(None, description="Optional broader document context, title, or clause metadata")
    mode: Literal["simple_english", "detailed", "professional"] = Field(
        default="simple_english",
        description="Explanation mode: simple_english (plain English), detailed (thorough breakdown), or professional (commercial executive)"
    )


class LLMSimplifyResult(BaseModel):
    explanation: str = Field(..., description="Simplified explanation in the requested mode, preserving conditions/exceptions")
    glossary: list[GlossaryTerm] = Field(default_factory=list, description="Key legal terms and concepts defined in plain language")
    what_could_be_missed: list[str] = Field(
        default_factory=list,
        description="Key nuances, hidden traps, procedural prerequisites, or strict deadlines that could be missed"
    )


class SimplifyResponse(BaseModel):
    original_text: str
    mode: str
    explanation: str
    glossary: list[GlossaryTerm] = Field(default_factory=list)
    what_could_be_missed: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    is_grounded: bool = True
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None

