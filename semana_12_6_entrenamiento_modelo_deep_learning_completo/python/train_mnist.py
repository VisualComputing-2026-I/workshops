"""Entrenamiento completo de un modelo de Deep Learning sobre MNIST.

El script cubre el flujo del taller: carga de datos, visualizacion,
entrenamiento, validacion, K-Fold, metricas, fine-tuning con ResNet18 y
guardado/reutilizacion del modelo.
"""

from __future__ import annotations

import argparse
import copy
import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import KFold
from torch.utils.data import DataLoader, Subset, random_split
from torchvision import datasets, models, transforms
from tqdm import tqdm


CLASS_NAMES = [str(i) for i in range(10)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Entrena y evalua modelos de clasificacion para MNIST."
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--model-dir", type=Path, default=Path("models"))
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--kfold-splits", type=int, default=5)
    parser.add_argument("--kfold-epochs", type=int, default=1)
    parser.add_argument("--kfold-samples", type=int, default=10000)
    parser.add_argument("--skip-kfold", action="store_true")
    parser.add_argument("--finetune-epochs", type=int, default=2)
    parser.add_argument("--finetune-samples", type=int, default=3000)
    parser.add_argument("--skip-finetune", action="store_true")
    parser.add_argument("--no-pretrained", action="store_true")
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Dispositivo de entrenamiento.",
    )
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def select_device(name: str) -> torch.device:
    if name == "cuda":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if name == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def make_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def load_mnist(data_dir: Path) -> tuple[datasets.MNIST, datasets.MNIST]:
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
        ]
    )
    train_data = datasets.MNIST(
        root=data_dir, train=True, download=True, transform=transform
    )
    test_data = datasets.MNIST(
        root=data_dir, train=False, download=True, transform=transform
    )
    print("Tamano del set de entrenamiento:", len(train_data))
    print("Tamano del set de prueba:", len(test_data))
    return train_data, test_data


def save_sample_image(dataset: datasets.MNIST, output_dir: Path) -> None:
    image, label = dataset[0]
    plt.figure(figsize=(4, 4))
    plt.imshow(image.squeeze(), cmap="gray")
    plt.title(f"Etiqueta: {label}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_dir / "sample_mnist.png", dpi=160)
    plt.close()


def create_loaders(
    train_data: datasets.MNIST,
    test_data: datasets.MNIST,
    batch_size: int,
    num_workers: int,
    seed: int,
) -> tuple[DataLoader, DataLoader, DataLoader]:
    train_size = int(0.8 * len(train_data))
    val_size = len(train_data) - train_size
    generator = torch.Generator().manual_seed(seed)
    train_subset, val_subset = random_split(
        train_data, [train_size, val_size], generator=generator
    )
    train_loader = DataLoader(
        train_subset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    val_loader = DataLoader(
        val_subset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    test_loader = DataLoader(
        test_data,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    return train_loader, val_loader, test_loader


def build_mlp() -> nn.Module:
    return nn.Sequential(
        nn.Flatten(),
        nn.Linear(28 * 28, 128),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Linear(64, 10),
    )


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
    description: str,
) -> float:
    model.train()
    running_loss = 0.0
    for images, labels in tqdm(loader, desc=description, leave=False):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    return running_loss / len(loader)


def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float, list[int], list[int]]:
    model.eval()
    total_loss = 0.0
    total = 0
    correct = 0
    all_preds: list[int] = []
    all_labels: list[int] = []

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            total_loss += criterion(outputs, labels).item()
            _, preds = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (preds == labels).sum().item()
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

    return total_loss / len(loader), correct / total, all_preds, all_labels


def train_mlp(
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int,
    lr: float,
    device: torch.device,
) -> tuple[nn.Module, list[float], list[float], list[float]]:
    model = build_mlp().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    train_losses: list[float] = []
    val_losses: list[float] = []
    val_accuracies: list[float] = []

    for epoch in range(epochs):
        train_loss = train_one_epoch(
            model, train_loader, criterion, optimizer, device, f"Epoch {epoch + 1}/{epochs}"
        )
        val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, device)
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)
        print(
            f"Epoch {epoch + 1}/{epochs} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val Accuracy: {val_acc:.4f}"
        )

    return model, train_losses, val_losses, val_accuracies


def plot_losses(train_losses: list[float], val_losses: list[float], output_dir: Path) -> None:
    plt.figure(figsize=(8, 5))
    plt.plot(train_losses, label="Entrenamiento")
    plt.plot(val_losses, label="Validacion")
    plt.xlabel("Epoca")
    plt.ylabel("Perdida")
    plt.title("Curvas de entrenamiento y validacion")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_dir / "loss_curves.png", dpi=160)
    plt.close()


def plot_confusion_matrix(
    labels: list[int], preds: list[int], output_dir: Path, filename: str = "confusion_matrix.png"
) -> None:
    cm = confusion_matrix(labels, preds)
    plt.figure(figsize=(8, 6))
    try:
        import seaborn as sns

        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
    except ImportError:
        plt.imshow(cm, cmap="Blues")
        plt.colorbar()
        for row in range(cm.shape[0]):
            for col in range(cm.shape[1]):
                plt.text(col, row, str(cm[row, col]), ha="center", va="center")
        plt.xticks(range(10), CLASS_NAMES)
        plt.yticks(range(10), CLASS_NAMES)
    plt.xlabel("Prediccion")
    plt.ylabel("Etiqueta real")
    plt.title("Matriz de confusion")
    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=160)
    plt.close()


def run_kfold(
    train_data: datasets.MNIST,
    splits: int,
    epochs: int,
    batch_size: int,
    num_workers: int,
    device: torch.device,
    seed: int,
    sample_limit: int,
    output_dir: Path,
) -> list[float]:
    total_samples = min(sample_limit, len(train_data)) if sample_limit > 0 else len(train_data)
    indices = np.arange(total_samples)
    kfold = KFold(n_splits=splits, shuffle=True, random_state=seed)
    fold_accuracies: list[float] = []
    criterion = nn.CrossEntropyLoss()

    print(f"\nValidacion K-Fold con {splits} folds y {total_samples} muestras.")
    for fold, (train_idx, val_idx) in enumerate(kfold.split(indices), start=1):
        train_subset = Subset(train_data, indices[train_idx].tolist())
        val_subset = Subset(train_data, indices[val_idx].tolist())
        train_loader = DataLoader(
            train_subset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
        )
        val_loader = DataLoader(
            val_subset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
        )
        model = build_mlp().to(device)
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        for epoch in range(epochs):
            train_one_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
                device,
                f"Fold {fold}/{splits} - Epoch {epoch + 1}/{epochs}",
            )
        _, accuracy, _, _ = evaluate(model, val_loader, criterion, device)
        fold_accuracies.append(accuracy)
        print(f"Fold {fold}: accuracy={accuracy:.4f}")

    plt.figure(figsize=(7, 4))
    plt.bar(range(1, splits + 1), fold_accuracies, color="#4C78A8")
    plt.axhline(np.mean(fold_accuracies), color="#F58518", linestyle="--", label="Promedio")
    plt.xlabel("Fold")
    plt.ylabel("Accuracy")
    plt.title("Resultados de validacion K-Fold")
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "fold_accuracies.png", dpi=160)
    plt.close()
    return fold_accuracies


def get_resnet_weights(use_pretrained: bool):
    if not use_pretrained:
        return None
    try:
        return models.ResNet18_Weights.DEFAULT
    except AttributeError:
        return "IMAGENET1K_V1"


def make_resnet(pretrained: bool, freeze_backbone: bool) -> nn.Module:
    weights = get_resnet_weights(pretrained)
    try:
        model = models.resnet18(weights=weights)
    except TypeError:
        model = models.resnet18(pretrained=pretrained)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 10)
    return model


def load_mnist_for_resnet(data_dir: Path) -> datasets.MNIST:
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.Grayscale(num_output_channels=3),
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ]
    )
    return datasets.MNIST(root=data_dir, train=True, download=True, transform=transform)


def train_resnet_variant(
    base_dataset: datasets.MNIST,
    sample_count: int,
    batch_size: int,
    num_workers: int,
    epochs: int,
    device: torch.device,
    pretrained: bool,
    freeze_backbone: bool,
    lr: float,
    seed: int,
    label: str,
) -> float:
    sample_count = min(sample_count, len(base_dataset))
    generator = torch.Generator().manual_seed(seed)
    selected, _ = random_split(
        base_dataset, [sample_count, len(base_dataset) - sample_count], generator=generator
    )
    train_size = int(0.8 * len(selected))
    val_size = len(selected) - train_size
    train_subset, val_subset = random_split(
        selected, [train_size, val_size], generator=torch.Generator().manual_seed(seed + 1)
    )
    train_loader = DataLoader(
        train_subset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    val_loader = DataLoader(
        val_subset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    model = make_resnet(pretrained=pretrained, freeze_backbone=freeze_backbone).to(device)
    params = [param for param in model.parameters() if param.requires_grad]
    optimizer = optim.Adam(params, lr=lr)
    criterion = nn.CrossEntropyLoss()

    print(f"\nEntrenando {label} con {sample_count} muestras.")
    best_acc = 0.0
    best_state = copy.deepcopy(model.state_dict())
    for epoch in range(epochs):
        train_one_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            device,
            f"{label} - Epoch {epoch + 1}/{epochs}",
        )
        _, accuracy, _, _ = evaluate(model, val_loader, criterion, device)
        if accuracy > best_acc:
            best_acc = accuracy
            best_state = copy.deepcopy(model.state_dict())
        print(f"{label} | Epoch {epoch + 1}/{epochs} | Val Accuracy: {accuracy:.4f}")

    model.load_state_dict(best_state)
    return best_acc


def run_finetuning_comparison(
    data_dir: Path,
    output_dir: Path,
    batch_size: int,
    num_workers: int,
    epochs: int,
    sample_count: int,
    device: torch.device,
    pretrained: bool,
    seed: int,
    mlp_test_accuracy: float,
) -> dict[str, float]:
    resnet_dataset = load_mnist_for_resnet(data_dir)
    frozen_acc = train_resnet_variant(
        resnet_dataset,
        sample_count,
        batch_size,
        num_workers,
        epochs,
        device,
        pretrained,
        freeze_backbone=True,
        lr=1e-4,
        seed=seed,
        label="ResNet18 capa final",
    )
    full_acc = train_resnet_variant(
        resnet_dataset,
        sample_count,
        batch_size,
        num_workers,
        epochs,
        device,
        pretrained,
        freeze_backbone=False,
        lr=1e-5,
        seed=seed,
        label="ResNet18 fine-tuning completo",
    )
    results = {
        "MLP MNIST": mlp_test_accuracy,
        "ResNet18 capa final": frozen_acc,
        "ResNet18 fine-tuning completo": full_acc,
    }

    plt.figure(figsize=(9, 4))
    names = list(results.keys())
    values = list(results.values())
    bars = plt.bar(names, values, color=["#4C78A8", "#54A24B", "#E45756"])
    plt.ylabel("Accuracy")
    plt.title("Comparacion de modelos")
    plt.ylim(0, 1)
    plt.xticks(rotation=12, ha="right")
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 0.01, f"{value:.3f}", ha="center")
    plt.tight_layout()
    plt.savefig(output_dir / "model_comparison.png", dpi=160)
    plt.close()
    return results


def save_metrics(metrics: dict, output_dir: Path) -> None:
    with (output_dir / "metrics.json").open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    make_dirs(args.output_dir, args.model_dir)
    device = select_device(args.device)
    print(f"Dispositivo usado: {device}")

    train_data, test_data = load_mnist(args.data_dir)
    save_sample_image(train_data, args.output_dir)
    train_loader, val_loader, test_loader = create_loaders(
        train_data, test_data, args.batch_size, args.num_workers, args.seed
    )

    model, train_losses, val_losses, val_accuracies = train_mlp(
        train_loader, val_loader, args.epochs, args.lr, device
    )
    plot_losses(train_losses, val_losses, args.output_dir)

    criterion = nn.CrossEntropyLoss()
    test_loss, test_accuracy, test_preds, test_labels = evaluate(
        model, test_loader, criterion, device
    )
    print("\nReporte de clasificacion en prueba:")
    print(classification_report(test_labels, test_preds, target_names=CLASS_NAMES))
    plot_confusion_matrix(test_labels, test_preds, args.output_dir)

    model_path = args.model_dir / "modelo_final.pth"
    torch.save(model.state_dict(), model_path)
    print(f"Modelo guardado en: {model_path}")

    reloaded_model = build_mlp().to(device)
    reloaded_model.load_state_dict(torch.load(model_path, map_location=device))
    reloaded_model.eval()
    print("Modelo recargado correctamente.")

    metrics: dict[str, object] = {
        "mlp": {
            "test_loss": test_loss,
            "test_accuracy": test_accuracy,
            "best_val_accuracy": max(val_accuracies),
        }
    }

    if not args.skip_kfold:
        fold_accuracies = run_kfold(
            train_data,
            args.kfold_splits,
            args.kfold_epochs,
            args.batch_size,
            args.num_workers,
            device,
            args.seed,
            args.kfold_samples,
            args.output_dir,
        )
        metrics["kfold"] = {
            "accuracies": fold_accuracies,
            "mean_accuracy": float(np.mean(fold_accuracies)),
            "std_accuracy": float(np.std(fold_accuracies)),
        }

    if not args.skip_finetune:
        comparison = run_finetuning_comparison(
            args.data_dir,
            args.output_dir,
            args.batch_size,
            args.num_workers,
            args.finetune_epochs,
            args.finetune_samples,
            device,
            pretrained=not args.no_pretrained,
            seed=args.seed,
            mlp_test_accuracy=test_accuracy,
        )
        metrics["comparison"] = comparison

    save_metrics(metrics, args.output_dir)
    print(f"Metricas guardadas en: {args.output_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
