from __future__ import annotations

from pathlib import Path
import csv

import torch
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset, TensorDataset

from digit_recognizer.config import DATASET_DIR, LOCAL_TEST_CSV, LOCAL_TRAIN_CSV, MODEL_PATH
from digit_recognizer.model import DigitCNN


class CsvDigitDataset(TensorDataset):
    @classmethod
    def from_file(cls, path: Path) -> "CsvDigitDataset":
        images = []
        labels = []
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.reader(file)
            for row_number, row in enumerate(reader, start=1):
                if len(row) != 785:
                    raise ValueError(f"{path} 第 {row_number} 行应包含 785 列，实际为 {len(row)} 列。")
                labels.append(int(row[0]))
                pixels = [float(value) / 255.0 for value in row[1:]]
                images.append(pixels)

        image_tensor = torch.tensor(images, dtype=torch.float32).view(-1, 1, 28, 28)
        label_tensor = torch.tensor(labels, dtype=torch.long)
        image_tensor = (image_tensor - 0.1307) / 0.3081
        return cls(image_tensor, label_tensor)


def train(epochs: int = 3, batch_size: int = 128, learning_rate: float = 1e-3) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_set, test_set, dataset_source = load_datasets()
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_set, batch_size=512)

    model = DigitCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * images.size(0)

        accuracy = evaluate(model, test_loader, device)
        average_loss = running_loss / len(train_loader.dataset)
        print(f"epoch={epoch} loss={average_loss:.4f} test_accuracy={accuracy:.4f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.cpu().state_dict(),
            "architecture": "DigitCNN",
            "dataset": dataset_source,
            "epochs": epochs,
            "normalization": {"mean": 0.1307, "std": 0.3081},
        },
        MODEL_PATH,
    )
    print(f"saved model to {MODEL_PATH}")


def load_datasets() -> tuple[Dataset, Dataset, str]:
    if LOCAL_TRAIN_CSV.exists() and LOCAL_TEST_CSV.exists():
        print(f"loading local csv datasets: {LOCAL_TRAIN_CSV.name}, {LOCAL_TEST_CSV.name}")
        return CsvDigitDataset.from_file(LOCAL_TRAIN_CSV), CsvDigitDataset.from_file(LOCAL_TEST_CSV), "local CSV MNIST"

    print("local CSV datasets not found, downloading MNIST with torchvision")
    from torchvision import datasets, transforms

    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,)),
        ]
    )
    train_set = datasets.MNIST(DATASET_DIR, train=True, download=True, transform=transform)
    test_set = datasets.MNIST(DATASET_DIR, train=False, download=True, transform=transform)
    return train_set, test_set, "torchvision MNIST"


def evaluate(model: DigitCNN, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            predictions = model(images).argmax(dim=1)
            correct += (predictions == labels).sum().item()
            total += labels.numel()
    return correct / total


if __name__ == "__main__":
    train()
