from flask import Flask, request, jsonify
import tflite_runtime.interpreter as tflite
from keras_image_helper import create_preprocessor

# Создаем Flask приложение
app = Flask(__name__)

# Создаем препроцессор
preprocessor = create_preprocessor('xception', target_size=(299, 299))

# Загрузка модели
interpreter = tflite.Interpreter(model_path='Deployment/clothing-model-v4-0.886.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
input_index = input_details[0]['index']

output_details = interpreter.get_output_details()
output_index = output_details[0]['index']

# Функция прогноза
def predict(X):
    interpreter.set_tensor(input_index, X)
    interpreter.invoke()

    preds = interpreter.get_tensor(output_index)
    return preds[0]

labels = [
    'dress',
    'hat',
    'longsleeve',
    'outwear',
    'pants',
    'shirt',
    'shoes',
    'shorts',
    'skirt',
    't-shirt'
]

# Функция раскодирования
def decode_predictions(pred):
    result = {c: float(p) for c, p in zip(labels, pred)}
    return result

# Обработчик HTTP-запроса
@app.route('/predict', methods=['POST'])
def handle_request():
    try:
        # Получаем URL изображения из запроса
        data = request.get_json()
        url = data['url']

        # Обрабатываем изображение и получаем прогноз
        X = preprocessor.from_url(url)
        preds = predict(X)
        results = decode_predictions(preds)

        # Возвращаем результат в формате JSON
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Запуск Flask-сервера
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)