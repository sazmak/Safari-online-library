import os
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, abort, current_app, send_from_directory, session
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from flask_babel import lazy_gettext as _l, gettext as _
from sqlalchemy.orm import selectinload
from werkzeug.utils import secure_filename

from .models import db, User, Resource, Comment, UserVote

bp = main = Blueprint("main", __name__)


# ── Category registry ─────────────────────────────────────────────────────────

CATEGORIES = [
    ("lecture", _l("Лекция")),
    ("book",    _l("Книга")),
    ("article", _l("Статья")),
    ("video",   _l("Видео")),
    ("task",    _l("Задание")),
    ("other",   _l("Другое")),
]


def _attach_labels(resources):
    category_map = {slug: str(label) for slug, label in CATEGORIES}
    for r in resources:
        r.category_label = category_map.get(r.category, r.category.capitalize())
    return resources


# ── Favicon ───────────────────────────────────────────────────────────────────

@main.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.png", mimetype="image/png",
    )


# ── Language switch ───────────────────────────────────────────────────────────

@main.route("/set_language/<lang>")
def set_language(lang):
    if lang in current_app.config.get("LANGUAGES", ["ru", "en", "kk"]):
        session["language"] = lang
    return redirect(request.referrer or url_for("main.index"))


# ── Index ─────────────────────────────────────────────────────────────────────

@main.route("/")
def index():
    q               = request.args.get("q", "").strip()
    active_category = request.args.get("category", "").strip()
    active_subject  = request.args.get("subject", "").strip()

    stmt = (
        db.select(Resource)
        .options(selectinload(Resource.comments))
        .order_by(Resource.timestamp.desc())
    )
    if q:
        like_q = f"%{q}%"
        stmt = stmt.where(
            Resource.title.ilike(like_q) |
            Resource.subject.ilike(like_q) |
            Resource.description.ilike(like_q)
        )
    if active_category:
        stmt = stmt.where(Resource.category == active_category)
    if active_subject:
        stmt = stmt.where(Resource.subject == active_subject)

    resources = _attach_labels(db.session.execute(stmt).scalars().all())
    subjects = sorted(
        db.session.execute(
            db.select(Resource.subject).where(Resource.subject.isnot(None)).distinct()
        ).scalars().all()
    )

    return render_template(
        "index.html", resources=resources, categories=CATEGORIES,
        subjects=subjects, active_category=active_category,
        active_subject=active_subject, search_query=q,
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
            flash(_("Заполните все обязательные поля."), "error")
            return render_template("add_resource.html", categories=CATEGORIES)

        db.session.add(Resource(
            title=title, link=link, category=category,
            subject=subject, description=description, user_id=current_user.id,
        ))
        db.session.commit()
        flash(_("Материал успешно добавлен!"), "success")
        return redirect(url_for("main.index"))

    return render_template("add_resource.html", categories=CATEGORIES)


# ── Delete resource ───────────────────────────────────────────────────────────

@main.route("/resource/<int:resource_id>/delete", methods=["POST"])
@login_required
def delete_resource(resource_id):
    resource = db.get_or_404(Resource, resource_id)
    if resource.user_id != current_user.id:
        abort(403)
    db.session.delete(resource)
    db.session.commit()
    flash(_("Материал удалён."), "info")
    return redirect(request.referrer or url_for("main.index"))


# ── Vote ──────────────────────────────────────────────────────────────────────

@main.route("/resource/<int:resource_id>/vote/<string:value>", methods=["POST"])
@login_required
def vote(resource_id, value):
    if value not in ("like", "dislike"):
        abort(400)

    resource = db.get_or_404(Resource, resource_id)
    existing = db.session.execute(
        db.select(UserVote).filter_by(user_id=current_user.id, resource_id=resource_id)
    ).scalar_one_or_none()

    if existing:
        if existing.value == value:
            if value == "like":
                resource.likes    = max(0, resource.likes - 1)
            else:
                resource.dislikes = max(0, resource.dislikes - 1)
            db.session.delete(existing)
        else:
            if value == "like":
                resource.likes    += 1
                resource.dislikes  = max(0, resource.dislikes - 1)
            else:
                resource.dislikes += 1
                resource.likes     = max(0, resource.likes - 1)
            existing.value = value
    else:
        if value == "like":
            resource.likes    += 1
        else:
            resource.dislikes += 1
        db.session.add(UserVote(
            user_id=current_user.id, resource_id=resource_id, value=value,
        ))

    db.session.commit()
    return redirect(request.referrer or url_for("main.index"))


# ── Comments ──────────────────────────────────────────────────────────────────

@main.route("/resource/<int:resource_id>/comment", methods=["POST"])
@login_required
def add_comment(resource_id):
    db.get_or_404(Resource, resource_id)
    text = request.form.get("text", "").strip()

    if not text:
        flash(_("Комментарий не может быть пустым."), "error")
    else:
        db.session.add(Comment(
            text=text, user_id=current_user.id, resource_id=resource_id,
        ))
        db.session.commit()

    return redirect(request.referrer or url_for("main.index"))


# ── Profile ───────────────────────────────────────────────────────────────────

@main.route("/profile/<username>")
def profile(username):
    user = db.first_or_404(db.select(User).filter_by(username=username))
    resources = _attach_labels(
        db.session.execute(
            db.select(Resource)
            .where(Resource.user_id == user.id)
            .options(selectinload(Resource.comments))
            .order_by(Resource.timestamp.desc())
        ).scalars().all()
    )
    return render_template(
        "profile.html", profile_user=user,
        resources=resources, categories=CATEGORIES,
    )


# ── Avatar upload ─────────────────────────────────────────────────────────────

@main.route("/profile/upload_avatar", methods=["POST"])
@login_required
def upload_avatar():
    file = request.files.get("avatar")
    if not file or file.filename == "":
        flash(_("Файл не выбран."), "error")
        return redirect(url_for("main.profile", username=current_user.username))

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    allowed = current_app.config.get("ALLOWED_AVATAR_EXTENSIONS", {"jpg", "jpeg", "png", "gif", "webp"})
    if ext not in allowed:
        flash(_("Недопустимый формат файла. Используйте JPG, PNG, GIF или WebP."), "error")
        return redirect(url_for("main.profile", username=current_user.username))

    filename = secure_filename(f"avatar_{current_user.id}.{ext}")
    save_dir = os.path.join(current_app.root_path, "static", "uploads", "avatars")
    os.makedirs(save_dir, exist_ok=True)

    if current_user.profile_picture and current_user.profile_picture != filename:
        old_path = os.path.join(save_dir, current_user.profile_picture)
        if os.path.exists(old_path):
            os.remove(old_path)

    file.save(os.path.join(save_dir, filename))
    current_user.profile_picture = filename
    db.session.commit()
    flash(_("Фото профиля обновлено!"), "success")
    return redirect(url_for("main.profile", username=current_user.username))


# ── Auth ──────────────────────────────────────────────────────────────────────

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        login_input = request.form.get("login", "").strip()
        password    = request.form.get("password", "")
        user = db.session.execute(
            db.select(User).where(
                (User.username == login_input) | (User.email == login_input)
            )
        ).scalar_one_or_none()

        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(request.args.get("next") or url_for("main.index"))

        flash(_("Неверное имя пользователя или пароль."), "error")

    return render_template("login.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower() or None
        password = request.form.get("password", "")

        username_taken = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()
        email_taken = email and db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if username_taken:
            flash(_("Это имя пользователя уже занято."), "error")
        elif email_taken:
            flash(_("Этот email уже зарегистрирован."), "error")
        elif len(username) < 3:
            flash(_("Имя пользователя должно содержать минимум 3 символа."), "error")
        elif len(password) < 6:
            flash(_("Пароль должен содержать минимум 6 символов."), "error")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash(_("Добро пожаловать, %(username)s!", username=username), "success")
            return redirect(url_for("main.index"))

    return render_template("register.html")


@main.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
