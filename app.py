from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.xception import preprocess_input
from PIL import Image
import numpy as np

# Загрузка модели
model = load_model('xception_v3_05_0.824.keras')

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

# Инициализация Flask приложения
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Функция проверки расширения файла
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Главная страница
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Проверка наличия файла в запросе
        if 'file' not in request.files:
            return 'Нет файла для загрузки'
        file = request.files['file']
        if file.filename == '':
            return 'Файл не выбран'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Сохранение пути к файлу в сессии или передача в шаблон
            return render_template('index.html', filename=filename)
    return render_template('index.html')

# Маршрут для предсказания
@app.route('/predict/<filename>')
def predict(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Шаг 1: Загрузка изображения
        img = Image.open(filepath).resize((150, 150))  # Изменение размера до 150x150 для Xception

        # Шаг 2: Преобразование изображения в массив Numpy
        x = np.array(img)

        # Шаг 3: Создание батча изображений
        X = np.array([x])  # Добавление измерения для батча

        # Шаг 4: Нормализация изображения
        X = preprocess_input(X)  # Функция из Keras для Xception

        # Шаг 5: Предсказание модели
        pred = model.predict(X)

        # Шаг 6: Определение метки класса
        predicted_label = labels[pred[0].argmax()]

        # Возврат результата
        return render_template('result.html', result=predicted_label)
    except Exception as e:
        return f"Ошибка при обработке изображения: {e}"

if __name__ == '__main__':
    app.run(debug=True)