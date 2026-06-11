from __future__ import annotations

from pathlib import Path


class PredictorUnavailable(RuntimeError):
    pass


class Predictor:
    def __init__(self, model_path: Path) -> None:
        try:
            import torch
        except ModuleNotFoundError as exc:
            raise PredictorUnavailable("缺少 PyTorch 依赖，请先安装 requirements.txt。") from exc

        from digit_recognizer.model import DigitCNN

        if not model_path.exists():
            raise PredictorUnavailable(f"未找到模型权重：{model_path}。请运行 python train.py。")

        self.torch = torch
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model = DigitCNN().to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

    def predict_pixels(self, pixels: list[object]) -> dict:
        from digit_recognizer.preprocessing import pixels_to_tensor

        tensor = pixels_to_tensor(pixels).to(self.device)
        with self.torch.no_grad():
            logits = self.model(tensor)
            probabilities = self.torch.softmax(logits, dim=1).squeeze(0).cpu().tolist()
        predicted_digit = int(max(range(10), key=lambda i: probabilities[i]))
        return {
            "predicted_digit": predicted_digit,
            "probabilities": [round(float(value), 6) for value in probabilities],
        }
