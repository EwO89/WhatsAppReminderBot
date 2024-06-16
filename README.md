# WhatsApp Reminder Bot

WhatsApp Reminder Bot - это приложение, созданное на базе FastAPI и Celery, которое использует Twilio для отправки напоминаний через WhatsApp.

## ТЗ
[Смотреть на гугл диск](https://docs.google.com/document/d/1GbAmRXWzPMxI-aeuYWF_92962LQ8WwYu/edit?usp=sharing&ouid=106308963898479999770&rtpof=true&sd=true)

## Краткое видео работы бота
[Видео в папке на гугл диск](https://drive.google.com/drive/folders/1tP7EQBeLUPQ4aaxGJX6E64jdfrjk6mZ-?usp=sharing)

## Используемые технологии

- **FastAPI**: асинхронный веб-фреймворк для создания API.
- **Celery**: система управления отложенными задачами.
- **Redis**: брокер сообщений и бэкенд для Celery.
- **Twilio**: платформа для отправки сообщений WhatsApp.
- **Docker**: контейнеризация приложений.
- **Pytest**: тестирование.
- **Ngrok**: публичный uri для обращения Twilio к нашему локальному приложению.

## Требования

- Docker и Docker Compose установлены на вашей машине.
- Учетная запись Twilio для отправки сообщений.
- Ngrok для связи Twilio с нашим локальным приложением

## Установка и запуск

### Шаг 1: Клонируйте репозиторий

```bash
git clone https://github.com/your-username/whatsapp-reminder-bot.git
cd whatsapp-reminder-bot
```

Шаг 2: Настройте переменные окружения
Создайте файл .env в корне проекта со следующим содержимым:
```env
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
TWILIO_WHATSAPP_NUMBER=whatsapp:your_twilio_whatsapp_number
HOST=0.0.0.0
PORT=8000
```

Шаг 3: Запустите приложение

Используйте Docker Compose для запуска всех сервисов:
```bash
docker-compose up --build
```
Приложение будет доступно по адресу http://localhost:8000

## API

Вебхуки
POST /webhooks/twilio
Используется Twilio для отправки сообщений. Пример тела запроса:
```json
{
  "From": "whatsapp:+1234567890",
  "Body": "/add remind me to buy groceries at 2024-06-16 21:00 in Europe/Moscow"
}
```
**Команды**

* /start: Начало работы с ботом. Отправляет приветственное сообщение и список доступных команд.
* /help: Показать список доступных команд.
* /list: Показать все текущие напоминания.
* /delete [ID or index]: Удалить конкретное напоминание по ID или индексу.
* /add remind me to [task] at [YYYY-MM-DD HH:MM] in [Timezone]: Добавить новое напоминание. 

## Тестирование

Для запуска тестов используйте Pytest. Убедитесь, что у вас установлен pytest-mock:
```bash
pip install pytest pytest-mock
```
Запустите тесты:
```bash
pytest src/tests
```
