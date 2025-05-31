import numpy as np
import torch
from PIL import Image

from .inference import BrainTumorClassifier
from .transforms import val_transform

# Dummy ONNX path for instantiation test (should be replaced with a real or mock model for real tests)
DUMMY_ONNX_PATH = "app/brain_tumor_classifier.onnx"


def test_val_transform_output_type():
    print("\nTesting val_transform output type...")
    transform = val_transform()
    img = Image.fromarray(np.uint8(np.random.rand(256, 256, 3) * 255))
    tensor = transform(img)
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape[1:] == (224, 224)
    print("✓ val_transform correctly returns torch.Tensor with shape (3, 224, 224)")


def test_classifier_instantiation_and_error():
    print("\nTesting classifier instantiation and error handling...")
    # Should not raise on instantiation
    model = BrainTumorClassifier(DUMMY_ONNX_PATH)
    # Should return error dict on bad input
    result = model.predict(None)  # type: ignore  # intentionally passing None to test error handling
    assert isinstance(result, dict)
    assert "status" in result and result["status"] == "Error"
    print("✓ Classifier instantiation successful")
    print("✓ Error handling works correctly with invalid input")


def test_predict_output_keys():
    print("\nTesting predict method output structure...")
    model = BrainTumorClassifier(DUMMY_ONNX_PATH)
    img = Image.fromarray(np.uint8(np.random.rand(256, 256, 3) * 255))
    result = model.predict(img)
    assert isinstance(result, dict)
    assert "predicted_class" in result
    assert "confidence" in result
    print("✓ predict method returns dictionary with required keys")
    print(f"  - predicted_class: {result['predicted_class']}")
    print(f"  - confidence: {result['confidence']:.4f}")


# To generate an HTML report, run:
# pytest --html=report.html --self-contained-html
