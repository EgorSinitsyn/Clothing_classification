from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.xception import preprocess_input
from PIL import Image
import numpy as np


# Загрузка модели
model = load_model('xception_v4_large_06_0.886.keras')

# Метки классов
labels = {
    0: 'dress',
    1: 'hat',
    2: 'longsleeve',
    3: 'outwear',
    4: 'pants',
    5: 'shirt',
    6: 'shoes',
    7: 'shorts',
    8: 'skirt',
    9: 't-shirt'
}

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    # Проверка наличия файла в запросе
    if 'file' not in request.files:
        return jsonify({'error': 'Нет файла для предсказания'}), 400

    file = request.files['file']
    if file:
        try:
            # Обработка изображения
            img = Image.open(file).resize((299, 299))
            x = np.array(img)
            X = np.expand_dims(x, axis=0)
            X = preprocess_input(X)

            # Предсказание
            pred = model.predict(X)
            predicted_label = labels[pred[0].argmax()]

            # Возврат результата
            return jsonify({'prediction': predicted_label})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Некорректный файл'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)