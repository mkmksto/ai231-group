import sys
sys.path.append("..")
from modules.model import TumorClassifier
from modules.train import train_model
from modules.transforms import train_transform, val_transform
from torch.utils.data import random_split, ConcatDataset, DataLoader
from torchvision import datasets
import torch
from datetime import datetime

CHECKPOINT_PATH = "../training_data/effnet_weights_sampler_cosine_best_model.pth"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def build_datasets():
    # Load dataset using ImageFolder
    train_dataset = datasets.ImageFolder(root="brain_tumor_dataset/Training", transform=train_transform())
    test_dataset = datasets.ImageFolder(root="brain_tumor_dataset/Testing", transform=train_transform())
    classes = test_dataset.classes
    full_dataset = ConcatDataset([train_dataset, test_dataset])

    train_dataset, test_dataset = random_split(
        full_dataset,
        [0.7, 0.3],
        generator=torch.Generator().manual_seed(42)
    )

    return train_dataset, test_dataset, classes

def model_init():
    model = TumorClassifier()
    model = model.to(DEVICE)
    model.load_state_dict(torch.load(CHECKPOINT_PATH))

    return model

def main():
    model = model_init()
    train_dataset, test_dataset, classes = build_datasets()

    date_str = datetime.now().strftime("%Y%m%d")
    model_name = f"effnet_feedback_retrain_{date_str}"

    train_model(
        model,
        train_dataset,
        batch_size=32,
        epochs=20,
        val_split=0.2,
        lr=0.001,
        save_path=model_name,
        use_sampler=True,
        scheduler_type="cosine",
    )

    evaluate_and_report(
        model,
        test_loader,
        device,
        classes,
    )
