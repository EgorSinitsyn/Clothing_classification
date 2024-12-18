import tensorflow as tf
from tensorflow import keras

# Путь к модели
model_path = '../xception_v4_large_06_0.886.keras'

# Проверяем на ошибку при загрузке модели
try:
    model = keras.models.load_model(model_path)
except ValueError as e:
    print(f"Error loading model: {e}")
    raise

# Конвертируем модель в формат TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with tf.io.gfile.GFile('Deployment_with_Docker/clothing-model-v4-0.886.tflite', 'wb') as f:
    f.write(tflite_model)
