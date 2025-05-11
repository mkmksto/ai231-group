import onnxruntime as ort
import numpy as np
from modules.transforms import val_transform
from PIL import Image
import time

class BrainTumorClassifier:
    def __init__(self, onnx_path):
        self.session = ort.InferenceSession(onnx_path)
        self.input_name = self.session.get_inputs()[0].name
        self.transform = val_transform()
        self.class_mapping = {
            0: 'glioma_tumor',
            1: 'meningioma_tumor',
            2: 'no_tumor',
            3: 'pituitary_tumor'
        }

    def _prepare_input(self, image: Image.Image):
        # Assumes transform returns a torch.Tensor
        return self.transform(image).unsqueeze(0).numpy()

    def predict(self, image: Image.Image):
        try:
            preprocess_start = time.time()
            input_data = self._prepare_input(image)
            preprocess_end = time.time()
            print(f"Preprocessing Time: {(preprocess_end - preprocess_start)*100:.3f} ms")
            
            start_event = time.time()
            outputs = self.session.run(None, {self.input_name: input_data})
 
            # Softmax
            probabilities = np.exp(outputs[0]) / np.sum(np.exp(outputs[0]), axis=1, keepdims=True)
            predicted_class = outputs[0].argmax().item()
            confidence = np.max(probabilities)
            end_event = time.time()

            print(f"Inference Time: {(end_event - start_event)*100:.3f} ms")
            return {
                "predicted_class": self.class_mapping[predicted_class],
                "confidence": confidence
            }

        except Exception as e:
            return {
                "status": "Error",
                "error_message": str(e)
            }
