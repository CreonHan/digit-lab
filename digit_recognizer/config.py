from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = ROOT_DIR / "data" / "app.db"
DATASET_DIR = ROOT_DIR / "datasets"
MODEL_PATH = ROOT_DIR / "artifacts" / "digit_cnn.pt"
LOCAL_TRAIN_CSV = ROOT_DIR / "train.csv"
LOCAL_TEST_CSV = ROOT_DIR / "test.csv"
