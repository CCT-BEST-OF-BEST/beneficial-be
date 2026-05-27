from pydantic import BaseModel, Field


class CardContentResponse(BaseModel):
    card_id: str
    word: str
    meaning: str | None = None
    example_sentence: str | None = None
    pronunciation: str | None = None
    visual_hint: str | None = None
    color_theme: str | None = None


class Stage1CardPairResponse(BaseModel):
    pair_id: str
    word1: str
    word2: str
    card1: CardContentResponse
    card2: CardContentResponse
    order: int


class Stage1CardsResponse(BaseModel):
    success: bool = True
    total_pairs: int
    card_pairs: list[Stage1CardPairResponse] = Field(default_factory=list)


class Stage1SubmitRequest(BaseModel):
    pair_id: str = Field(..., description="카드 쌍 ID (예: pair_1)")
    chosen_word: str = Field(..., description="학생이 고른 단어 (word1 또는 word2)")


class Stage1SubmitResponse(BaseModel):
    pair_id: str
    is_correct: bool
    chosen_word: str
    correct_word: str
    concept_key: str
