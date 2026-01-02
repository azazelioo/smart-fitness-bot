# 🏋️ Smart Fitness Assistant

Telegram-бот для персональных фитнес-тренировок с анализом питания на основе нейросети.

## Возможности

- 📊 **Профиль** — расчёт BMR, TDEE, целевого калоража
- 🏋️ **Тренировки** — персональные программы (50+ упражнений)
- 🍽 **Анализ питания** — распознавание еды по фото (MobileNetV2)
- 📈 **Статистика** — отслеживание прогресса

## 🚀 Быстрый старт

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/YOUR_USERNAME/smart-fitness-bot.git
cd smart-fitness-bot
```

### 2. Настройте окружение
```bash
cp .env.example .env
# Отредактируйте .env — добавьте BOT_TOKEN и DATABASE_URL
```

### 3. Запуск с Docker
```bash
docker-compose up -d
```

### 4. Или локально
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
python -m bot.main
```

## ⚙️ Переменные окружения

| Переменная | Описание |
|------------|----------|
| `BOT_TOKEN` | Токен от [@BotFather](https://t.me/BotFather) |
| `DATABASE_URL` | URL базы данных (SQLite или PostgreSQL) |

**Примеры DATABASE_URL:**
```
# SQLite (локально):
sqlite+aiosqlite:///./fitness_bot.db

# PostgreSQL (Supabase):
postgresql+asyncpg://postgres:password@db.xxx.supabase.co:5432/postgres
```

## 🏗 Структура проекта

```
smart_fitness_bot/
├── bot/
│   ├── handlers/      # Обработчики команд
│   ├── keyboards/     # Клавиатуры
│   └── main.py        # Точка входа
├── database/
│   ├── models.py      # SQLAlchemy модели
│   ├── database.py    # Подключение
│   └── crud.py        # CRUD операции
├── modules/
│   ├── anthropometry.py
│   ├── training_generator.py
│   └── food_analyzer/
│       ├── model.py   # MobileNetV2 классификатор
│       └── nutrition_db.py
├── config.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 🧠 Обучение нейросети

Модель обучена на датасете Food-101 (101 категория блюд).

Для обучения своей модели:
1. Используйте `modules/food_analyzer/train_food_classifier.ipynb` в Google Colab
2. Скачайте `food_model_best.pth`
3. Положите в `modules/food_analyzer/`

## 📦 Деплой

### Railway
1. Создайте проект на [railway.app](https://railway.app)
2. Подключите GitHub репозиторий
3. Добавьте переменные окружения
4. Deploy!

### Render
1. Создайте Web Service на [render.com](https://render.com)
2. Подключите репозиторий
3. Dockerfile будет обнаружен автоматически

## 👤 Автор

Горбунов Демид Александрович, БИВ251  
НИУ ВШЭ МИЭМ

---
📌 *Курсовая работа по направлению 09.03.01 Информатика и вычислительная техника*
