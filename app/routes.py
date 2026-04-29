import os
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, abort, current_app
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from .models import db, User, Resource, CATEGORIES, Comment, UserVote

bp = main = Blueprint('main', __name__)


# ── Category registry ─────────────────────────────────────────────────────────
CATEGORIES = [
    ("lecture", "Лекция"),
    ("book",    "Книга"),
    ("article", "Статья"),
    ("video",   "Видео"),
    ("task",    "Задание"),
    ("other",   "Другое"),
]
CATEGORY_MAP = {slug: label for slug, label in CATEGORIES}


def _attach_labels(resources):
    """Add a .category_label attribute to each resource object."""
    for r in resources:
        r.category_label = CATEGORY_MAP.get(r.category, r.category.capitalize())
    return resources


# ── Index ─────────────────────────────────────────────────────────────────────

@main.route("/")
def index():
    q               = request.args.get("q", "").strip()
    active_category = request.args.get("category", "").strip()
    active_subject  = request.args.get("subject", "").strip()

    query = Resource.query

    if q:
        like_q = f"%{q}%"
        query = query.filter(
            Resource.title.ilike(like_q) |
            Resource.subject.ilike(like_q) |
            Resource.description.ilike(like_q)
        )
    if active_category:
        query = query.filter_by(category=active_category)
    if active_subject:
        query = query.filter_by(subject=active_subject)

    resources = _attach_labels(
        query.order_by(Resource.timestamp.desc()).all()
    )

    # Unique subjects for the sidebar pill list
    subjects = sorted({
        r.subject for r in Resource.query.filter(Resource.subject.isnot(None)).all()
        if r.subject
    })

    return render_template(
        "index.html",
        resources=resources,
        categories=CATEGORIES,
        subjects=subjects,
        active_category=active_category,
        active_subject=active_subject,
        search_query=q,
    )


# ── Add resource ──────────────────────────────────────────────────────────────

@main.route("/add", methods=["GET", "POST"])
@login_required
def add_resource():
    if request.method == "POST":
        title       = request.form.get("title", "").strip()
        link        = request.form.get("link", "").strip()
        category    = request.form.get("category", "").strip()
        subject     = request.form.get("subject", "").strip() or None
        description = request.form.get("description", "").strip() or None

        if not title or not link or not category:
            flash("Заполните все обязательные поля.", "error")
            return render_template("add_resource.html", categories=CATEGORIES)

        resource = Resource(
            title=title,
            link=link,
            category=category,
            subject=subject,
            description=description,
            user_id=current_user.id,
        )
        db.session.add(resource)
        db.session.commit()
        flash("Материал успешно добавлен!", "success")
        return redirect(url_for("main.index"))

    return render_template("add_resource.html", categories=CATEGORIES)


# ── Delete resource ───────────────────────────────────────────────────────────

@main.route("/resource/<int:resource_id>/delete", methods=["POST"])
@login_required
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if resource.user_id != current_user.id:
        abort(403)
    db.session.delete(resource)
    db.session.commit()
    flash("Материал удалён.", "info")
    # Return to referer if possible
    return redirect(request.referrer or url_for("main.index"))


# ── Vote (like / dislike) ─────────────────────────────────────────────────────

@main.route("/resource/<int:resource_id>/vote/<string:value>", methods=["POST"])
@login_required
def vote(resource_id, value):
    if value not in ("like", "dislike"):
        abort(400)

    resource = Resource.query.get_or_404(resource_id)
    existing = UserVote.query.filter_by(
        user_id=current_user.id, resource_id=resource_id
    ).first()

    if existing:
        if existing.value == value:
            # Toggle off: remove the vote
            if value == "like":
                resource.likes    = max(0, resource.likes - 1)
            else:
                resource.dislikes = max(0, resource.dislikes - 1)
            db.session.delete(existing)
        else:
            # Switch vote direction
            if value == "like":
                resource.likes    += 1
                resource.dislikes  = max(0, resource.dislikes - 1)
            else:
                resource.dislikes += 1
                resource.likes     = max(0, resource.likes - 1)
            existing.value = value
    else:
        # New vote
        if value == "like":
            resource.likes    += 1
        else:
            resource.dislikes += 1
        vote_obj = UserVote(
            user_id=current_user.id,
            resource_id=resource_id,
            value=value,
        )
        db.session.add(vote_obj)

    db.session.commit()
    return redirect(request.referrer or url_for("main.index"))


# ── Comments ──────────────────────────────────────────────────────────────────

@main.route("/resource/<int:resource_id>/comment", methods=["POST"])
@login_required
def add_comment(resource_id):
    Resource.query.get_or_404(resource_id)  # 404 guard
    text = request.form.get("text", "").strip()

    if not text:
        flash("Комментарий не может быть пустым.", "error")
    else:
        comment = Comment(
            text=text,
            user_id=current_user.id,
            resource_id=resource_id,
        )
        db.session.add(comment)
        db.session.commit()

    return redirect(request.referrer or url_for("main.index"))


# ── Profile ───────────────────────────────────────────────────────────────────

@main.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    resources = _attach_labels(
        Resource.query
        .filter_by(user_id=user.id)
        .order_by(Resource.timestamp.desc())
        .all()
    )
    return render_template(
        "profile.html",
        profile_user=user,
        resources=resources,
        categories=CATEGORIES,
    )


# ── Avatar upload ─────────────────────────────────────────────────────────────

@main.route("/profile/upload_avatar", methods=["POST"])
@login_required
def upload_avatar():
    file = request.files.get("avatar")
    if not file or file.filename == "":
        flash("Файл не выбран.", "error")
        return redirect(url_for("main.profile", username=current_user.username))

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    allowed = current_app.config.get("ALLOWED_AVATAR_EXTENSIONS", {"jpg", "jpeg", "png", "gif", "webp"})
    if ext not in allowed:
        flash("Недопустимый формат файла. Используйте JPG, PNG, GIF или WebP.", "error")
        return redirect(url_for("main.profile", username=current_user.username))

    filename = secure_filename(f"avatar_{current_user.id}.{ext}")
    save_dir = os.path.join(current_app.root_path, "static", "uploads", "avatars")
    os.makedirs(save_dir, exist_ok=True)

    # Remove old avatar file if extension changed
    if current_user.profile_picture and current_user.profile_picture != filename:
        old_path = os.path.join(save_dir, current_user.profile_picture)
        if os.path.exists(old_path):
            os.remove(old_path)

    file.save(os.path.join(save_dir, filename))
    current_user.profile_picture = filename
    db.session.commit()
    flash("Фото профиля обновлено!", "success")
    return redirect(url_for("main.profile", username=current_user.username))


# ── Auth ──────────────────────────────────────────────────────────────────────

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(request.args.get("next") or url_for("main.index"))

        flash("Неверное имя пользователя или пароль.", "error")

    return render_template("login.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if User.query.filter_by(username=username).first():
            flash("Это имя пользователя уже занято.", "error")
        elif len(username) < 3:
            flash("Имя пользователя должно содержать минимум 3 символа.", "error")
        elif len(password) < 6:
            flash("Пароль должен содержать минимум 6 символов.", "error")
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash(f"Добро пожаловать, {username}!", "success")
            return redirect(url_for("main.index"))

    return render_template("register.html")


@main.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))