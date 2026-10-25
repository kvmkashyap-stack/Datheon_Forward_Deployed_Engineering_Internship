
from enterprise_rag.conversation.intent_router import get_conversation_response


def test_hi_gets_a_greeting() -> None:
    response = get_conversation_response("Hi")
    assert response is not None
    assert "Enterprise RAG Assistant" in response


def test_hello_with_punctuation() -> None:
    assert get_conversation_response("Hello!") is not None


def test_how_are_you_gets_a_conversational_response() -> None:
    response = get_conversation_response("How are you?")
    assert response is not None
    assert "thanks for asking" in response


def test_capabilities_question_is_handled() -> None:
    assert get_conversation_response("What can you do?") is not None


def test_agreement_question_stays_on_rag_path() -> None:
    assert (
        get_conversation_response(
            "What are the termination conditions in the agreement?"
        )
        is None
    )


def test_greeting_plus_document_question_stays_on_rag_path() -> None:
    assert (
        get_conversation_response(
            "Hi, what are the termination conditions?"
        )
        is None
    )


def test_empty_message_is_not_a_conversation_response() -> None:
    assert get_conversation_response("   ") is None
