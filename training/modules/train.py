import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, WeightedRandomSampler
from .transforms import val_transform
import os

# EarlyStopping Class
class EarlyStopping:
    def __init__(self, patience=5):
        self.patience = patience
        self.counter = 0
        self.best_loss = float('inf')
        self.early_stop = False

    def step(self, val_loss):
        if val_loss < self.best_loss:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        return self.early_stop

def train_model(
    model,
    dataset,
    batch_size=32,
    epochs=20,
    val_split=0.2,
    lr=0.001,
    save_path=None,
    use_sampler=False,
    scheduler_type="steplr",
    patience=5,  # EarlyStopping patience
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    # 1. Split dataset
    val_size = int(len(dataset) * val_split)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    val_dataset.dataset.transform = val_transform()

    # 2. Sampler for class balancing (optional)
    if use_sampler:
        targets = [dataset[i][1] for i in train_dataset.indices]  # Correctly fetch labels
        class_counts = torch.bincount(torch.tensor(targets))
        class_weights = 1.0 / class_counts.float()
        sample_weights = [class_weights[t] for t in targets]
        sampler = WeightedRandomSampler(sample_weights, len(sample_weights))

        train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler,
                                  num_workers=min(4, os.cpu_count()))
    else:
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True,
                                  num_workers=min(4, os.cpu_count()))

    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False,
                            num_workers=min(4, os.cpu_count()))

    # 3. Optimizer, Loss, Scheduler
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    if scheduler_type.lower() == "steplr":
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=4, gamma=0.5)
    elif scheduler_type.lower() == "cosine":
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    else:
        scheduler = None

    # 4. Training loop
    train_losses, val_losses = [], []
    train_accuracies, val_accuracies = [], []
    early_stopper = EarlyStopping(patience=patience)
    best_val_acc = 0.0

    for epoch in range(epochs):
        model.train()
        running_loss, correct, total = 0.0, 0, 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

            if scheduler is not None:
                scheduler.step()  # Move scheduler step here if you want per-iteration scheduler (optional)

        epoch_loss = float(running_loss) / total
        epoch_acc = correct / total
        train_losses.append(epoch_loss)
        train_accuracies.append(epoch_acc)

        # Validation
        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)

        val_loss /= val_total
        val_acc = val_correct / val_total
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)

        # Scheduler step (preferred here: after one epoch)
        if scheduler is not None:
            scheduler.step()

        print(f"Epoch [{epoch+1}/{epochs}] - "
              f"Train Loss: {epoch_loss:.4f}, Train Acc: {epoch_acc:.4f} - "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")

        # Save best model based on validation accuracy
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            if save_path:
                torch.save(model.state_dict(), save_path)

        # Early stopping
        if early_stopper.step(val_loss):
            print(f"Early stopping triggered at epoch {epoch+1}")
            break

    return train_losses, val_losses, train_accuracies, val_accuracies
