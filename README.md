# 🦁 Safari Digital Library

![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

> **🌍 Live Demo:** (https://safari-online-library.onrender.com/)

**Safari Digital Library** is an aesthetic and functional knowledge base designed for teams and students. It eliminates the chaos of losing important links in messenger chats by providing a structured, centralized platform for educational resources.

> **The Problem:** Educational materials (lectures, books, articles, videos) often get lost in infinite chat histories.
> **The Solution:** A unified hub with smart filtering and a premium *Editorial Dark* design.

---

## ✨ Key Features

* 🌑 **Premium UI/UX:** High-end dark interface featuring "Glassmorphism" effects and golden accents.
* 🔍 **Smart Discovery:** Instant filtering by title, author, or category.
* 👍 **Interactive System:** Like/Dislike functionality to highlight the most valuable resources.
* 💬 **Engaging Discussions:** A dedicated comment section for every resource to facilitate feedback.
* 👤 **User Profiles:** Personalized dashboards where authors can manage their uploaded content.
* 📱 **Fully Responsive:** Optimized for everything from 4K monitors to mobile screens.

---

## 🛠 Tech Stack

* **Backend:** Python 3.10+, Flask (Application Factory Pattern)
* **Database & ORM:** SQLAlchemy with support for SQLite (local) and PostgreSQL (production).
* **Authentication:** Flask-Login with secure password hashing.
* **Frontend:** Jinja2 templates, Modern Vanilla CSS (Variables, Flexbox, Grid), and JavaScript for interactive elements.

---

## 📂 Project Structure

```text
SAFARI-ONLINE-LIBRARY/
├── app/                     # Main application package
│   ├── static/              # Static assets (Custom CSS, JS, Avatars)
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── _card.html       # Reusable resource card component
│   │   └── ...              # Page templates (index, profile, login, etc.)
│   ├── __init__.py          # App factory & extension initialization
│   ├── models.py            # SQLAlchemy database models
│   └── routes.py            # Application routing & business logic
├── instance/                # Local data storage (SQLite)
├── config.py                # Environment-based configurations
├── run.py                   # Application entry point
├── requirements.txt         # Project dependencies
└── render.yaml              # Deployment configuration for Render.com
```

---

## 🚀 Quick Start

### 1. Environment Setup
Clone the repository and create a virtual environment:
```bash
git clone [https://github.com/sazmak/Safari-online-library.git](https://github.com/sazmak/Safari-online-library.git)
cd Safari-online-library
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
The database will be initialized automatically on the first run:
```bash
python run.py
```
Access the local server at: `http://127.0.0.1:5000`

---

## 👥 Team
Developed with ❤️ by **SAFARI-team** for the Ed-Tech Challenge.
*Created to ensure that knowledge is never lost, only shared.*



---




# 🦁 Safari Digital Library

![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

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
*Проект создан для того, чтобы знания не терялись, а множились.*


