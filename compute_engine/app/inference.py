import time

import numpy as np
import onnxruntime as ort
from PIL import Image

from app.transforms import val_transform


class BrainTumorClassifier:
    def __init__(self, onnx_path):
        self.session = ort.InferenceSession(onnx_path)
        self.input_name = self.session.get_inputs()[0].name
        self.transform = val_transform()
        self.class_mapping = {
            0: "glioma_tumor",
            1: "meningioma_tumor",
            2: "no_tumor",
            3: "pituitary_tumor",
        }

    def _prepare_input(self, image: Image.Image):
        # Assumes transform returns a torch.Tensor
        return self.transform(image).unsqueeze(0).numpy()

    def predict(self, image: Image.Image):
        try:
            preprocess_start = time.time()
            input_data = self._prepare_input(image)
            preprocess_end = time.time()
            print(
                f"Preprocessing Time: {(preprocess_end - preprocess_start) * 100:.3f} ms"
            )

            start_event = time.time()
            outputs = self.session.run(None, {self.input_name: input_data})
            logits = outputs[0]

            # Softmax
            probabilities = np.exp(logits) / np.sum(
                np.exp(logits), axis=1, keepdims=True
            )
            predicted_class = np.argmax(probabilities, axis=1)[0]
            confidence = float(probabilities[0][predicted_class])
            end_event = time.time()

            print(f"Inference Time: {(end_event - start_event) * 100:.3f} ms")
            return {
                "predicted_class": self.class_mapping[predicted_class],
                "confidence": confidence,
            }

        except Exception as e:
            return {"status": "Error", "error_message": str(e)}
