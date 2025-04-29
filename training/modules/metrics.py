import torch
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import seaborn as sns

@torch.no_grad()
def evaluate_and_report(model, dataloader, device, class_names, plot_roc=True):
    """
    Evaluate model, print classification report, test accuracy, confusion matrix, and plot ROC curves.

    Args:
        model: Trained model
        dataloader: DataLoader for testing
        device: torch.device
        class_names: List of class names
        plot_roc: Whether to plot ROC curves (default True)

    Returns:
        all_preds, all_labels, all_probs
    """

    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []

    # 3. Evaluation loop
    for images, labels in dataloader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        probs = torch.softmax(outputs, dim=1)
        preds = torch.argmax(probs, dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        all_probs.extend(probs.cpu().numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)

    # 4. Classification Report
    print("\n=== Classification Report ===")
    print(classification_report(all_labels, all_preds, target_names=class_names))

    # 5. Test Accuracy
    test_acc = (all_preds == all_labels).mean()
    print(f"\n=== Test Accuracy: {test_acc*100:.2f}% ===")

    # 6. Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.tight_layout()
    plt.show()

    # 7. ROC Curves
    if plot_roc:
        plt.figure(figsize=(8, 6))
        for i in range(len(class_names)):
            fpr, tpr, _ = roc_curve(all_labels == i, all_probs[:, i])
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, label=f"{class_names[i]} (AUC = {roc_auc:.2f})")

        plt.plot([0, 1], [0, 1], 'k--')  # Diagonal
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves (One-vs-Rest)')
        plt.legend(loc="lower right")
        plt.grid()
        plt.show()

    return all_preds, all_labels, all_probs
