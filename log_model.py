import mlflow
import mlflow.keras
from tensorflow.keras.models import load_model
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Установка трекингового URI
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))


def log_model():
    # Загрузка вашей обученной модели
    model = load_model('xception_v4_large_06_0.886.keras')

    with mlflow.start_run() as run:
        mlflow.keras.log_model(model, "model")
        mlflow.log_params({
            # Добавьте параметры модели, если есть
            "model_name": "XceptionModel",
            "version": "v1"
        })
        mlflow.log_metric("accuracy", 0.886)  # Пример метрики
        print(f"Модель залогирована с Run ID: {run.info.run_id}")


if __name__ == "__main__":
    log_model()