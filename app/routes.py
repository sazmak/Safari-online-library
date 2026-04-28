from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, abort
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from sqlalchemy import or_

from .models import db, User, Resource, CATEGORIES

bp = main = Blueprint('main', __name__)


# ── Auth ─────────────────────────────────────────────────────────────────────

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm',  '')

        if not username or not password:
            flash('Заполните все поля.', 'error')
        elif password != confirm:
            flash('Пароли не совпадают.', 'error')
        elif len(password) < 6:
            flash('Пароль должен быть не менее 6 символов.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Этот email уже зарегистрирован.', 'error')
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Добро пожаловать в библиотеку!', 'success')
            return redirect(url_for('main.index'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Неверный email или пароль.', 'error')

    return render_template('login.html')


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))


# ── Main / Index ──────────────────────────────────────────────────────────────

@bp.route('/')
def index():
    category = request.args.get('category', '').strip()
    subject  = request.args.get('subject',  '').strip()
    query    = request.args.get('q',        '').strip()

    resources_q = Resource.query.order_by(Resource.timestamp.desc())

    if category:
        resources_q = resources_q.filter(Resource.category == category)

    if subject:
        resources_q = resources_q.filter(Resource.subject == subject)

    if query:
        like = f'%{query}%'
        resources_q = resources_q.filter(
            or_(
                Resource.title.ilike(like),
                Resource.description.ilike(like),
                Resource.subject.ilike(like),
            )
        )

    resources = resources_q.all()

    # Sidebar data
    all_subjects = (
        db.session.query(Resource.subject)
        .filter(Resource.subject.isnot(None), Resource.subject != '')
        .distinct()
        .order_by(Resource.subject)
        .all()
    )
    subjects = [s[0] for s in all_subjects]

    return render_template(
        'index.html',
        resources=resources,
        categories=CATEGORIES,
        subjects=subjects,
        active_category=category,
        active_subject=subject,
        search_query=query,
    )


# ── Add Resource ──────────────────────────────────────────────────────────────

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_resource():
    if request.method == 'POST':
        title       = request.form.get('title',       '').strip()
        link        = request.form.get('link',        '').strip()
        category    = request.form.get('category',    'other').strip()
        subject     = request.form.get('subject',     '').strip()
        description = request.form.get('description', '').strip()

        errors = []
        if not title:
            errors.append('Введите название материала.')
        if not link:
            errors.append('Введите ссылку.')
        elif not (link.startswith('http://') or link.startswith('https://')):
            errors.append('Ссылка должна начинаться с http:// или https://')

        valid_cats = [c[0] for c in CATEGORIES]
        if category not in valid_cats:
            category = 'other'

        if errors:
            for e in errors:
                flash(e, 'error')
        else:
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
            flash('Материал успешно добавлен!', 'success')
            return redirect(url_for('main.index'))

    return render_template('add_resource.html', categories=CATEGORIES)


# ── Delete Resource ───────────────────────────────────────────────────────────

@bp.route('/delete/<int:resource_id>', methods=['POST'])
@login_required
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if resource.user_id != current_user.id:
        abort(403)
    db.session.delete(resource)
    db.session.commit()
    flash('Материал удалён.', 'success')
    return redirect(url_for('main.index'))
