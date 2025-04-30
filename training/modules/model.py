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

def modify_mbconv_blocks(model):
    """
    Insert additional BatchNorm2d and Swish (SiLU) layers into each MBConv block of EfficientNet.
    """
    for name, module in model.named_modules():
        if isinstance(module, nn.Sequential):
            for idx, block in enumerate(module):
                if hasattr(block, 'block') and isinstance(block.block, nn.Sequential):
                    # Insert after depthwise convolution
                    for sub_idx, layer in enumerate(block.block):
                        if isinstance(layer, nn.Conv2d) and layer.groups == layer.in_channels:
                            # Depthwise conv found
                            bn = nn.BatchNorm2d(layer.out_channels)
                            swish = nn.SiLU()
                            # Insert BatchNorm + Swish immediately after depthwise conv
                            block.block.insert(sub_idx + 1, bn)
                            block.block.insert(sub_idx + 2, swish)
                            break
    return model


class TumorClassifierMBConv(nn.Module):
    def __init__(
        self,
        num_classes: int = 4,
        pretrained_model: nn.Module = None,
        weights: str = None,
        use_internal_modifications: bool = True,  # <<< NEW
    ):
        super().__init__()

        if pretrained_model is None:
            self.base_model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        else:
            self.base_model = pretrained_model
            if weights:
                try:
                    self.base_model.load_state_dict(torch.load(weights))
                except Exception as e:
                    print(f"Failed to load weights: {e}")

        # === Inject internal modifications if enabled ===
        if use_internal_modifications:
            self.base_model.features = modify_mbconv_blocks(self.base_model.features)

        # Get number of features based on model architecture
        if hasattr(self.base_model, "classifier"):
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
        return x

