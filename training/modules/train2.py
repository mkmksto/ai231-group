import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, WeightedRandomSampler
from collections import Counter
from modules.transforms import val_transform
import numpy as np


def mixup_data(x, y, alpha=0.4):
    '''Apply MixUp'''
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    batch_size = x.size(0)
    index = torch.randperm(batch_size).to(x.device)

    mixed_x = lam * x + (1 - lam) * x[index, :]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam

def train_model2(
    model,
    dataset,
    batch_size=32,
    epochs=20,
    val_split=0.2,
    lr=0.001,
    save_path=None,
    use_sampler=False,
    scheduler_type="steplr",
    use_mixup=False,
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Split into train and validation sets
    val_size = int(len(dataset) * val_split)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    val_dataset.dataset.transform = val_transform()

    # Compute class weights from training data
    train_labels = [dataset[i][1] for i in train_dataset.indices]
    class_counts = Counter(train_labels)
    class_weights = torch.tensor(
        [1.0 / class_counts[i] for i in range(len(class_counts))],
        dtype=torch.float
    ).to(device)

    # DataLoader setup
    if use_sampler:
        targets = [dataset[i][1] for i in train_dataset.indices]
        class_sample_count = torch.tensor([class_counts[t] for t in targets], dtype=torch.float)
        weights = 1. / class_sample_count
        sampler = WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler)
    else:
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.1)
    optimizer = optim.Adam(model.parameters(), lr=lr)

    if scheduler_type == "steplr":
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
    elif scheduler_type == "cosine":
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    else:
        scheduler = None

    model.to(device)

    best_acc = 0.0
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()

            # Apply MixUp if enabled
            if use_mixup:
                inputs, targets_a, targets_b, lam = mixup_data(inputs, labels)
                outputs = model(inputs)
                loss = lam * criterion(outputs, targets_a) + (1 - lam) * criterion(outputs, targets_b)
            else:
                outputs = model(inputs)
                loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        train_acc = correct / total

        # Validation phase
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        val_acc = val_correct / val_total
        print(f"Epoch {epoch+1}/{epochs} - Loss: {running_loss:.4f} - Train Acc: {train_acc:.4f} - Val Acc: {val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            if save_path:
                torch.save(model.state_dict(), save_path)

        if scheduler:
            scheduler.step()

    print("\nTraining complete. Best Val Acc: {:.4f}".format(best_acc))