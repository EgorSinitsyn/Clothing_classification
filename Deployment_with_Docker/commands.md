# Создание контейнера Docker:
1) Создание Dockerfile
2) Создание образа докер
```bash
docker build -t yandex-cloud-function .
```
4) Запуск контейнера
```bash
docker run -p 8080:8080 yandex-cloud-function
```


# Развертывание контейнера в Yandex Cloud на VM :

## Предварительная настройка YC
1) Установкa Yandex cli
2) Инициализация
```bash
yc init
```
3) Создание реестра контейнеров
```bash
yc container registry create --name my-registry
```
4) Настройка Docker для работы с contaner registry
```bash
yc container registry configure-docker
```

## Настройка сервисного аккаунта в YC
1) Создаю сервисный акк
yc iam service-account create --name my-service-account
2) Вывожу список командой
yc iam service-account list
3) Получаю айдишник
yc iam service-account get --name my-service-account
4) Назначаю роль editor

5) yc resource-manager folder add-access-binding \
    --id b1glbenc2rk9432smmsf \
    --role editor \
    --subject serviceAccount:aje3su5n5pno9fno757g

6) yc container registry add-access-binding \
    --name my-registry \
    --role container-registry.images.puller \
    --subject serviceAccount:aje3su5n5pno9fno757g
7) 

## Развертывание образа Docker
1) Тэгирую образ
```bash
docker tag yandex-cloud-function cr.yandex/crpqp4fj3ofoe6rvbmfh/yandex-cloud-function
```
2) Пуш обаза
```bash
docker push cr.yandex/crpqp4fj3ofoe6rvbmfh/yandex-cloud-function
```

## Настройка VM для деплоя
1) создать VM и подключиться по ssh
2) Установка докера и настройка службы инициализации
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
```
3) Настройте Docker для доступа к реестру Yandex Cloud
* На локальной машине выполняю
```bash 
yc container registry configure-docker
```
* На удаленном сервере выполняю
```bash 
sudo mkdir -p /home/host/.docker
sudo mkdir -p /root/.docker
```
* Копирую конфиг на машину
```bash
scp -i <путь до ключа> ~/.docker/config.json <your-user>@<vm-ip>:/home/<your-user>/.docker/config.json
```
* Перемещаю конфиг в папку рут
```bash
sudo mv /home/host/.docker/config.json /root/.docker/config.json
```
yc compute instance update \
    --name compute-vm-2-2-20-hdd-1733416804312 \
    --service-account-id aje3su5n5pno9fno757g



echo <Oauth-токен>|docker login \
  --username oauth \
  --password-stdin \
 cr.yandex



Проверка ролей и политик

yc container registry list-access-bindings --name my-registryy


yc container image list --registry-name my-registry



