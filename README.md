# Веб-приложение для автоматической классификации одежды

Данный проект представляет собой веб-приложение, которое позволяет пользователям загружать изображения элементов гардероба и получать предсказания с использованием заранее обученной модели машинного обучения.

Модель обучена предсказывать следующие элементы гардероба:

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

## Архитектура проекта

    clothing-classification-app/
    │
    │── clothing-dataset-small/  # Скаченный датасет с картинками (см. clothing-traing.ipynb)
    │── Deployment/              # Преобразование модели, подготовка Docker-образа, тестирование и развертывание
    ├── app.py                   # Главное приложение
    ├── model_service.py         # Микросервис модели
    ├── log_model.py             # Загрузка модели в MLFLOW
    ├── register_model_mlflow.py # Регистрация модели в MLFLOW
    ├── requirements.txt         # Зависимости проекта
    ├── .env                     # Переменные окружения от СУБД (not committed)
    ├── templates/
    │   ├── index.html           # Темплейт главной страницы
    │   └── result.html          # Темплейт предсказания
    ├── static/
    │   ├── uploads/             # Ваши загруженные изображения
    │── clothing-train.ipynb     # Пошаговая обработка данных, обчение и оценка моделей
    │── clothing-test.ipynb      # Пошаговое тестирование моделей на тестовом множестве
    └── README.md                # Описание проекта

1.	Основное приложение (app.py): Обрабатывает взаимодействие с пользователем, загрузку файлов и общается с микросервисом модели для получения предсказаний.
2.  Микросервис модели (model_service.py): Инкапсулирует модель машинного обучения и обрабатывает запросы на предсказание.
3.  Процесс обработки данных, обучения и оценки моделей в файлах: clothing-test.ipynb , clothing-train.ipynb 
4.  Deployment: Процесс преобразования модели, подготовки Docker-образа, тестирования и развертывания
5.  DB_init.py: Инициализация БД с нужной структурой
6.  log_model.py: Загрузка модели в MLFLOW
7.  register_model_mlflow.py: Регистрация модели в MLFLOW


## Установка

1. Клонирование репозитория
```bash
git clone https://github.com/EgorSinitsyn/Clothing_classification
cd Clothing_classification/
```
2. Настройка виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate  # Для Windows используйте `venv\Scripts\activate`
```
3. Установка зависимостей
```bash
pip install -r requirements.txt
```
4. Установка СУБД MySQL (см. документацию)
6. Создайте файл .env в корне проекта, поместите туда креды от СУБД MySQL
    
 ```   
    DB_HOST=localhost
    DB_PORT=3306
    DB_USER=<ваш_пользователь>
    DB_PASSWORD=<ваш_пароль>
    DB_NAME=clothing_classification
```
7. Инициализируйте БД с нужной структурой 
```bash
python DB_init.py
```
    P.S Отдэбажьте ошибки в случае их возникновения

8. Запустите MLFLOw на 5005 порту
```bash
mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5005
````
Откройте http://127.0.0.1:5005 для проверки службы MLFLOW

9. Загрузите модель в MLFLOW
```bash
python log_model.py
```

10. Зарегистрируйте модель в MLFLOW
```bash
python register_model_mlflow.py
```

11. Запустите приложение и микросервис модели (порты 5000 и 5001)
```bash
python model_serice.py
python app.py
```

12. Откройте http://127.0.0.1:5001 и пользуйтесь приложением