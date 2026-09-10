"""Загрузка и инференс модели bitfount/RETFound_MAE_OCT_CNV_DME_DRU.

Модель дообучена на датасете Kermany (OCT B-сканы сетчатки) под 4 класса.
Лицензия весов — CC BY-NC 4.0 (только некоммерческое использование).

Порядок классов и препроцессинг взяты из рабочего референсного инференса
(HF Space hadi6681/oct4class, использующий эту же модель):
https://huggingface.co/spaces/hadi6681/oct4class/blob/main/app.py
"""

import io

import numpy as np
import timm
import torch
from huggingface_hub import hf_hub_download
from PIL import Image

MODEL_REPO = "bitfount/RETFound_MAE_OCT_CNV_DME_DRU"
ARCH = "vit_large_patch16_224"
CLASSES = ["CNV", "DME", "DRUSEN", "NORMAL"]

IMG_SIZE = 224
MEAN = (0.5, 0.5, 0.5)
STD = (0.5, 0.5, 0.5)
CROP_PCT = 0.9
RESIZE_TO = round(IMG_SIZE / CROP_PCT)

_model: torch.nn.Module | None = None


def _load_model() -> torch.nn.Module:
    model = timm.create_model(ARCH, num_classes=len(CLASSES), global_pool="token", pretrained=False)
    ckpt_path = hf_hub_download(repo_id=MODEL_REPO, filename="pytorch_model.bin")
    state = torch.load(ckpt_path, map_location="cpu")
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    state = {(k[7:] if k.startswith("module.") else k): v for k, v in state.items()}
    model.load_state_dict(state, strict=False)
    model.eval()
    return model


def get_model() -> torch.nn.Module:
    global _model
    if _model is None:
        _model = _load_model()
    return _model


def _preprocess(image: Image.Image) -> torch.Tensor:
    image = image.convert("RGB")
    image = image.resize((RESIZE_TO, RESIZE_TO), Image.BICUBIC)
    left = (RESIZE_TO - IMG_SIZE) // 2
    top = (RESIZE_TO - IMG_SIZE) // 2
    image = image.crop((left, top, left + IMG_SIZE, top + IMG_SIZE))
    array = np.asarray(image).astype("float32") / 255.0
    array = (array - np.array(MEAN, dtype="float32")) / np.array(STD, dtype="float32")
    tensor = torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0)
    return tensor


@torch.no_grad()
def classify(image_bytes: bytes) -> tuple[str, float]:
    image = Image.open(io.BytesIO(image_bytes))
    tensor = _preprocess(image)
    logits = get_model()(tensor)
    probs = torch.softmax(logits, dim=1)[0].tolist()
    best_idx = max(range(len(CLASSES)), key=lambda i: probs[i])
    return CLASSES[best_idx], round(probs[best_idx], 4)
