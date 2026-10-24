from unittest.mock import Mock, patch

import numpy as np
import pytest

from legacyai.embeddings import embed_query, embed_texts


def test_embed_texts_returns_vectors():
    fake_model = Mock()
    fake_model.encode.return_value = np.array(
        [
            [0.6, 0.8],
            [1.0, 0.0],
        ]
    )

    with patch(
        "legacyai.embeddings.get_embedding_model",
        return_value=fake_model,
    ):
        result = embed_texts(["employee leave policy", "salary policy"])

    assert result == [
        [0.6, 0.8],
        [1.0, 0.0],
    ]

    fake_model.encode.assert_called_once_with(
        ["employee leave policy", "salary policy"],
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


def test_empty_input_returns_empty_list():
    with patch("legacyai.embeddings.get_embedding_model") as mock_loader:
        result = embed_texts([])

    assert result == []
    mock_loader.assert_not_called()


def test_empty_text_is_rejected():
    with pytest.raises(ValueError, match="Cannot embed empty text"):
        embed_texts(["valid text", "   "])


def test_embed_query_returns_single_vector():
    fake_model = Mock()
    fake_model.encode.return_value = np.array([[0.3, 0.4]])

    with patch(
        "legacyai.embeddings.get_embedding_model",
        return_value=fake_model,
    ):
        result = embed_query("What is the leave policy?")

    assert result == [0.3, 0.4]


def test_empty_query_is_rejected():
    with pytest.raises(ValueError, match="Query cannot be empty"):
        embed_query("   ")