import mlflow
from mlflow.tracking import MlflowClient
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Установка трекингового URI
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

client = MlflowClient()
model_name = "XceptionModel"

# Создание зарегистрированной модели, если она ещё не существует
try:
    client.create_registered_model(model_name)
    print(f"Создана зарегистрированная модель: {model_name}")
except Exception as e:
    print(f"Модель {model_name} уже существует. Пропускаем создание. Ошибка: {e}")

# Получение последнего Run для модели
runs = client.search_runs(experiment_ids=["0"], order_by=["attributes.start_time DESC"], max_results=1)
if not runs:
    print("Нет доступных Run для регистрации модели.")
    exit(1)

run = runs[0]
model_uri = f"runs:/{run.info.run_id}/model"

# Регистрация модели
model_version = client.create_model_version(model_name, model_uri, run.info.run_id)
print(f"Модель зарегистрирована как версия {model_version.version}")