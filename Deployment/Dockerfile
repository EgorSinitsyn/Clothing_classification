FROM python:3.7-slim

# Обновление pip
RUN pip3 install --upgrade pip

# Установка зависимостей
RUN pip3 install flask keras_image_helper tflite-runtime==2.11.0 --no-cache-dir

# Копирование модели и функции
COPY clothing-model-v4-0.886.tflite clothing-model-v4-0.886.tflite
COPY lambda_function.py lambda_function.py

# Указание команды для запуска
CMD ["python3", "lambda_function.py"]