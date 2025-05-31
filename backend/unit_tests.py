import pytest
from app import utils
from app.models import FeedbackInput
from pydantic import ValidationError


def test_feedback_input_valid():
    print("Testing valid feedback input...")
    data = {"image_id": "img123", "label": "glioma_tumor"}
    feedback = FeedbackInput(**data)
    print(
        f"Created feedback with image_id: {feedback.image_id}, label: {feedback.label}"
    )
    assert feedback.image_id == "img123"
    assert feedback.label == "glioma_tumor"
    print("Valid feedback input test passed")


def test_feedback_input_invalid():
    print("Testing invalid feedback input...")
    # Pydantic will raise ValidationError for missing required fields
    with pytest.raises(ValidationError):
        FeedbackInput()  # type: ignore  # missing required fields is intentional for this test
    print("Invalid feedback input test passed")
