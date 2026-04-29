# 🦁 Safari Digital Library

![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLachemy](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

**Сыллка на сайт** - https://safari-online-library.onrender.com/

**Safari Digital Library** — это эстетичная и функциональная база знаний для команд и студентов. Забудьте о потере ссылок в бесконечных чатах мессенджеров. Теперь все ваши учебные ресурсы структурированы и всегда под рукой.

> **Проблема:** Учебные материалы (лекции, статьи, видео) теряются в потоке сообщений.
> **Решение:** Единая платформа с умной фильтрацией и премиальным дизайном в стиле *Editorial Dark*.

---

## ✨ Ключевые возможности

* 🌑 **Premium UI/UX:** Интерфейс в глубоких темных тонах с золотыми акцентами и эффектом Glassmorphism.
* 🔍 **Умный поиск:** Мгновенная фильтрация по названию, автору или теме.
* 🗂 **Категоризация:** Четкое разделение контента на лекции, книги, статьи и видео с цветовой индикацией.
* 🔐 **Система авторизации:** Личный кабинет для управления своими публикациями.
* 📱 **Полный Responsive:** Идеальное отображение как на 4K мониторах, так и на экранах смартфонов.

---

## 🛠 Технологический стек

* **Core:** Python 3.10+, Flask
* **Database:** SQLAlchemy (SQLite)
* **Auth:** Flask-Login + Werkzeug
* **Frontend:** Jinja2, Modern Vanilla CSS (Variables, Flexbox, Grid)

---

## 📂 Структура проекта

```text
safari_library/
├── app/
│   ├── static/css/style.css  # Авторский дизайн (Dark Editorial)
│   ├── templates/            # Jinja2 шаблоны (Base, Index, Auth)
│   ├── models.py             # Схема БД (User, Resource)
│   └── routes.py             # Бизнес-логика приложения
├── instance/                 # Локальное хранилище БД
├── run.py                    # Точка входа в приложение
└── requirements.txt          # Зависимости проекта
```

---

## 🚀 Быстрый старт

### 1. Подготовка окружения
Клонируйте репозиторий и создайте виртуальное окружение:
```bash
git clone [https://github.com/sazmak/ed-Tech-Challange-SAFARI-team.git](https://github.com/sazmak/ed-Tech-Challange-SAFARI-team.git)
cd ed-Tech-Challange-SAFARI-team
python -m venv venv
source venv/bin/activate  # Для Windows: .\venv\Scripts\activate
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Инициализация базы данных
Выполните команды в консоли Python:
```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
```

### 4. Запуск
```bash
python run.py
```
Сайт будет доступен по адресу: `http://127.0.0.1:5000`

---

## 👥 Команда
Разработано с любовью командой **SAFARI-team** в рамках Ed-Tech Challenge.

---
*Проект создан для того, чтобы знания не терялись, а множились.*


