# Подготовка к запуску LocalStack

LocalStack — это инструмент с открытым исходным кодом, который эмулирует AWS-сервисы локально. Он работает через Docker, поэтому вам нужно установить Docker на свою машину.

## Требования

- **Docker**: Убедитесь, что Docker установлен и запущен.
  - Установка на Ubuntu:
    ```bash
    sudo apt update && sudo apt install docker.io
Установка на macOS/Windows: Скачайте и установите Docker Desktop с официального сайта.
Проверьте:
bash

Свернуть

Перенос

Копировать
docker --version
Python: Нужен для установки CLI LocalStack (опционально, но удобно).
Убедитесь, что Python установлен:
bash

Свернуть

Перенос

Копировать
python3 --version
pip: Для установки зависимостей Python.
Установка:
bash

Свернуть

Перенос

Копировать
sudo apt install python3-pip
Установка LocalStack
Установите LocalStack CLI:
bash

Свернуть

Перенос

Копировать
pip3 install localstack
Проверьте установку:
bash

Свернуть

Перенос

Копировать
localstack --version
Запустите LocalStack: LocalStack запускается в Docker-контейнере. Выполните команду:
bash

Свернуть

Перенос

Копировать
localstack start -d
Флаг -d запускает LocalStack в фоновом режиме.
После запуска проверьте статус:
bash

Свернуть

Перенос

Копировать
localstack status services
Вы увидите список сервисов, включая s3, со статусом available или running.
Если Docker не запущен, вы получите ошибку вроде "Cannot connect to the Docker daemon". В этом случае запустите Docker:
bash

Свернуть

Перенос

Копировать
sudo systemctl start docker
(на Linux) или откройте Docker Desktop.
Настройка S3 локально
После запуска LocalStack S3 будет доступен по адресу http://localhost:4566. Теперь нужно создать бакет и протестировать его.

1. Установите AWS CLI (если ещё не установлено)
AWS CLI позволяет взаимодействовать с LocalStack так же, как с реальным AWS S3.

bash

Свернуть

Перенос

Копировать
pip3 install awscli
aws --version
2. Настройте AWS CLI для LocalStack
Создайте профиль для работы с локальным S3:

bash

Свернуть

Перенос

Копировать
aws configure --profile localstack
Введите следующие значения:

AWS Access Key ID: test (любой, LocalStack не проверяет реальные ключи).
AWS Secret Access Key: test
Default region name: us-east-1 (или другой регион, но это не важно для LocalStack).
Default output format: json (или оставьте пустым).
3. Создайте S3-бакет
bash

Свернуть

Перенос

Копировать
aws --endpoint-url=http://localhost:4566 s3 mb s3://my-local-bucket --profile localstack
--endpoint-url указывает, что запрос идёт к LocalStack, а не к AWS.
Вывод: make_bucket: my-local-bucket.
4. Загрузите файл в бакет
Создайте тестовый файл:

bash

Свернуть

Перенос

Копировать
echo "Hello, LocalStack!" > test.txt
Загрузите его:

bash

Свернуть

Перенос

Копировать
aws --endpoint-url=http://localhost:4566 s3 cp test.txt s3://my-local-bucket/test.txt --profile localstack
Вывод: upload: ./test.txt to s3://my-local-bucket/test.txt.

5. Проверьте содержимое бакета
bash

Свернуть

Перенос

Копировать
aws --endpoint-url=http://localhost:4566 s3 ls s3://my-local-bucket --profile localstack
Вывод покажет test.txt с датой и размером.

6. Скачайте файл обратно
bash

Свернуть

Перенос

Копировать
aws --endpoint-url=http://localhost:4566 s3 cp s3://my-local-bucket/test.txt downloaded.txt --profile localstack
Проверьте содержимое:

bash

Свернуть

Перенос

Копировать
cat downloaded.txt
Интеграция с вашим ботом
Чтобы ваш Telegram-бот работал с локальным S3, настройте boto3 (Python SDK для AWS) для подключения к LocalStack.

Установите boto3:
bash

Свернуть

Перенос

Копировать
pip3 install boto3
Пример кода в handlers.py:
python

Свернуть

Перенос

Копировать
import boto3

# Настройка клиента S3 для LocalStack
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

# Пример загрузки фото в S3
@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    photo = message.photo[-1]
    file_id = photo.file_id
    file_path = f"temp/{file_id}.jpg"
    await photo.download(destination_file=file_path)
    
    # Загрузка в локальный S3
    s3_client.upload_file(file_path, 'my-local-bucket', f"photos/{file_id}.jpg")
    await message.reply(f"Фото загружено в S3: {file_id}")
    
    # Удаление временного файла
    os.remove(file_path)
Добавьте этот обработчик в register_handlers(dp) в handlers.py.

Дополнительные шаги по устранению ошибок
Если вы видите ошибку вроде ❌ Error: could not connect to LocalStack health endpoint at http://localhost.localstack.cloud:4566:

1. Проверьте статус Docker-контейнера
bash

Свернуть

Перенос

Копировать
docker ps -a
Найдите контейнер localstack_main. Если он в статусе Exited, посмотрите логи:

bash

Свернуть

Перенос

Копировать
docker logs localstack_main
2. Перезапустите LocalStack
bash

Свернуть

Перенос

Копировать
localstack stop
docker rm localstack_main
localstack start -d
3. Проверьте доступность
Подождите 20-30 секунд и выполните:

bash

Свернуть

Перенос

Копировать
localstack status services
Или:

bash

Свернуть

Перенос

Копировать
curl http://localhost:4566/health
Если возвращается JSON с информацией о сервисах, LocalStack работает корректно.

4. Создайте бакет для теста
bash

Свернуть

Перенос

Копировать
aws --endpoint-url=http://localhost:4566 s3 mb s3://my-local-bucket
aws --endpoint-url=http://localhost:4566 s3 ls