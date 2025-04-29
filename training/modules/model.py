import torch
import torch.nn as nn
from torchvision import models
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

class TumorClassifier(nn.Module):
    def __init__(
        self,
        num_classes: int = 4,
        pretrained_model: nn.Module = None,
        weights: str = None,
    ):
        super().__init__()

        # Use provided model or default to EfficientNetB0
        if pretrained_model is None:
            self.base_model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        else:
            self.base_model = pretrained_model
            if weights:
                try:
                    self.base_model.load_state_dict(torch.load(weights))
                except Exception as e:
                    print(f"Failed to load weights: {e}")

        # Get number of features based on model architecture
        if isinstance(self.base_model, models.mobilenet.MobileNetV3):
            num_features = self.base_model.classifier[-1].in_features
            self.base_model = nn.Sequential(
                self.base_model.features,
                self.base_model.avgpool,
                nn.Flatten(),
            )
        elif hasattr(self.base_model, "fc"):
            num_features = self.base_model.fc.in_features
            self.base_model = nn.Sequential(*list(self.base_model.children())[:-2])
        elif hasattr(self.base_model, "classifier"):
            num_features = self.base_model.classifier[-1].in_features
            self.base_model = nn.Sequential(*list(self.base_model.children())[:-1])
        else:
            raise ValueError("Unsupported model architecture")

        # Custom classifier
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(p=0.5),
            nn.Linear(num_features, num_classes),
        )

    def forward(self, x):
        x = self.base_model(x)
        x = self.classifier(x)
        return x  # <--- Output raw logits, no softmax inside
