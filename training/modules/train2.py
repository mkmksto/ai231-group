import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, WeightedRandomSampler
from collections import Counter
from modules.transforms import val_transform
import numpy as np
import torch.nn.functional as F


def mixup_data(inputs, targets, alpha=0.2, device='cuda', num_classes=4):
    '''Returns mixed inputs, mixed targets (soft labels), and lambda'''
    if alpha > 0:
        lam = torch.distributions.Beta(alpha, alpha).sample().item()
    else:
        lam = 1

    # Convert targets list to tensor if needed
    if isinstance(targets, list):
        targets = torch.tensor(targets)

    targets = targets.to(device)  # move to GPU if needed

    batch_size = inputs.size(0)
    index = torch.randperm(batch_size).to(device)

    mixed_inputs = lam * inputs + (1 - lam) * inputs[index, :]

    targets_onehot = F.one_hot(targets, num_classes=num_classes).float()
    targets_onehot_shuffled = F.one_hot(targets[index], num_classes=num_classes).float()

    mixed_targets = lam * targets_onehot + (1 - lam) * targets_onehot_shuffled

    return mixed_inputs, mixed_targets, lam


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
    
    if use_mixup:
        criterion = torch.nn.BCEWithLogitsLoss()
    else:
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
                inputs, targets, lam = mixup_data(inputs, targets, alpha=0.2, device=device)
                outputs = model(inputs)
                loss = criterion(outputs, targets)

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



def train_model3(
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
    fine_tune_at_epoch=5,
    hybrid=False
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # --- Data preparation ---
    val_size = int(len(dataset) * val_split)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    val_dataset.dataset.transform = val_transform()

    train_labels = [dataset[i][1] for i in train_dataset.indices]
    class_counts = Counter(train_labels)

    class_weights = torch.tensor(
        [1.0 / class_counts[i] for i in range(len(class_counts))],
        dtype=torch.float, device=device
    )

    if use_sampler:
        targets = [dataset[i][1] for i in train_dataset.indices]
        sample_weights = 1. / torch.tensor([class_counts[t] for t in targets], dtype=torch.float)
        sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler)
    else:
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # --- Model, Loss, Optimizer, Scheduler setup ---
    if hybrid:
        for param in model.backbone.parameters():
            param.requires_grad = False
    else:
        for param in model.base_model.parameters():
            param.requires_grad = False

    model.to(device)
    if use_mixup:
        criterion = torch.nn.BCEWithLogitsLoss()
    else:
        criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.1)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = {
        "steplr": optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5),
        "cosine": optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    }.get(scheduler_type, None)

    best_acc = 0.0

    # --- Training loop ---
    for epoch in range(epochs):
        model.train()
        running_loss, correct, total = 0.0, 0, 0

        # Unfreeze deeper layers at fine-tune epoch
        if epoch == fine_tune_at_epoch:
            print(f"Epoch {epoch+1}: Unfreezing deeper layers for fine-tuning...")
            if hybrid:
                # Unfreeze last 2 blocks
                backbone_blocks = list(model.backbone.children())
                for block in backbone_blocks[-3:]:
                    for param in block.parameters():
                        param.requires_grad = True
            else:    
                for param in model.base_model[-3:].parameters():
                    param.requires_grad = True
            optimizer = optim.Adam(model.parameters(), lr=lr * 0.1)
            scheduler = {
                "steplr": optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5),
                "cosine": optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs - fine_tune_at_epoch)
            }.get(scheduler_type, None)

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()

            if use_mixup:
                inputs, targets, lam = mixup_data(inputs, labels, alpha=0.2, device=device)
                outputs = model(inputs)
                loss = criterion(outputs, targets)
            else:
                outputs = model(inputs)
                loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)

        train_acc = correct / total

        # --- Validation phase ---
        model.eval()
        val_correct, val_total = 0, 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                val_correct += (outputs.argmax(1) == labels).sum().item()
                val_total += labels.size(0)

        val_acc = val_correct / val_total
        print(f"Epoch {epoch+1}/{epochs} - Loss: {running_loss:.4f} - Train Acc: {train_acc:.4f} - Val Acc: {val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            if save_path:
                torch.save(model.state_dict(), save_path)

        if scheduler:
            scheduler.step()

    print(f"\nTraining complete. Best Val Acc: {best_acc:.4f}")

