from app.domains.content.stage1.schemas import CardContentResponse, Stage1CardPairResponse


def stage1_pair_response(pair: dict) -> Stage1CardPairResponse:
    return Stage1CardPairResponse(
        pair_id=pair["pair_id"],
        word1=pair["word1"],
        word2=pair["word2"],
        card1=card_content_response(pair.get("card1", {}), pair["word1"]),
        card2=card_content_response(pair.get("card2", {}), pair["word2"]),
        order=pair["order"],
    )


def card_content_response(card: dict, word: str) -> CardContentResponse:
    return CardContentResponse(
        card_id=card.get("card_id", word),
        word=card.get("word", word),
        meaning=card.get("meaning"),
        example_sentence=card.get("example_sentence"),
        pronunciation=card.get("pronunciation"),
        visual_hint=card.get("visual_hint") or visual_hint_for_word(word),
        color_theme=card.get("color_theme") or color_theme_for_word(word),
    )


def visual_hint_for_word(word: str) -> str:
    hints = {
        "가르치다": "book-open",
        "가르키다": "hand-point-up",
        "맞추다": "puzzle",
        "맞히다": "target",
        "잊다": "brain",
        "잃다": "search-x",
        "메다": "backpack",
        "매다": "link",
        "바라다": "sparkles",
        "바래다": "palette",
        "부치다": "send",
        "붙이다": "paperclip",
        "되다": "check-circle",
        "돼다": "circle-alert",
        "안": "minus-circle",
        "않다": "ban",
        "반드시": "badge-check",
        "반듯이": "ruler",
        "이따가": "clock",
        "있다가": "map-pin",
    }
    return hints.get(word, "book-open")


def color_theme_for_word(word: str) -> str:
    primary_words = {
        "가르치다",
        "맞히다",
        "잊다",
        "메다",
        "바라다",
        "부치다",
        "되다",
        "안",
        "반드시",
        "이따가",
    }
    return "primary" if word in primary_words else "warning"
