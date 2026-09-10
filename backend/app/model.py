"""Загрузка и инференс модели tomalmog/oct-retinal-classifier.

MIT-лицензия (коммерческое использование разрешено), дообучена на
датасете Kermany2018 под 4 класса. Архитектура и препроцессинг взяты
из рабочего model.py в самом репозитории модели:
https://huggingface.co/tomalmog/oct-retinal-classifier/blob/main/model.py
"""

import io
import os
import urllib.request

import timm
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

MODEL_URL = "https://huggingface.co/tomalmog/oct-retinal-classifier/resolve/main/pytorch_model.bin"
CACHE_PATH = os.path.join(os.path.expanduser("~/.cache/octera-model"), "oct-retinal-classifier.bin")
CLASSES = ["CNV", "DME", "DRUSEN", "NORMAL"]

_transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


class OCTClassifier(nn.Module):
    """EfficientNet-B3 backbone + кастомная классификационная голова."""

    def __init__(self):
        super().__init__()
        self.backbone = timm.create_model("efficientnet_b3", pretrained=False, num_classes=0, global_pool="")
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(p=0.3),
            nn.Linear(1536, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.15),
            nn.Linear(512, 4),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.backbone(x)
        features = self.global_pool(features)
        return self.classifier(features)


_model: OCTClassifier | None = None


def _download_weights() -> str:
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    if not os.path.exists(CACHE_PATH):
        urllib.request.urlretrieve(MODEL_URL, CACHE_PATH)
    return CACHE_PATH


def _load_model() -> OCTClassifier:
    weights_path = _download_weights()
    model = OCTClassifier()
    state_dict = torch.load(weights_path, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()
    return model


def get_model() -> OCTClassifier:
    global _model
    if _model is None:
        _model = _load_model()
    return _model


@torch.no_grad()
def classify(image_bytes: bytes) -> tuple[str, float]:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = _transform(image).unsqueeze(0)
    logits = get_model()(tensor)
    probs = torch.softmax(logits, dim=1)[0].tolist()
    best_idx = max(range(len(CLASSES)), key=lambda i: probs[i])
    return CLASSES[best_idx], round(probs[best_idx], 4)
