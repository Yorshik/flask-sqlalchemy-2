import datetime

from flask import Flask, redirect, render_template
from flask_login import LoginManager, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, EmailField, PasswordField, BooleanField, StringField, IntegerField, DateField
from wtforms.validators import DataRequired, EqualTo

from data.db_session import create_session, global_init
from data.jobs import Jobs
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    again_pass = PasswordField(
        'Повтор', validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают')]
        )
    position = StringField('Должность', validators=[DataRequired()])
    speciality = StringField('Специальности', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class WorkForm(FlaskForm):
    job = StringField('Работа', validators=[DataRequired()])
    work_size = IntegerField('Размер работы (часы)', validators=[DataRequired()])
    start_date = DateField('Начало', validators=[DataRequired()])
    end_date = DateField('Конец', validators=[DataRequired()])
    collaborators = StringField('Коллабораторы', validators=[DataRequired()])
    teamleader = IntegerField('Тимлид', validators=[DataRequired()])
    is_finished = BooleanField('Работа закончена?')
    submit = SubmitField('Добавить')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/add_work', methods=['GET', 'POST'])
def add_work():
    form = WorkForm()
    if form.validate_on_submit():
        db_sess = create_session()
        job = Jobs()
        job.job = form.job.data
        job.team_leader = form.teamleader.data
        job.work_size = form.work_size.data
        job.start_date = form.start_date.data
        job.end_date = form.end_date.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        db_sess.add(job)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    return render_template('work.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    sess = create_session()
    form = RegisterForm()
    if form.is_submitted():
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.set_password(form.password.data)
        user.address = form.address.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.age = form.age.data
        user.modified_date = datetime.datetime.now()
        sess.add(user)
        sess.commit()
        sess.refresh(user)
        sess.close()
        login_user(user, remember=True, duration=datetime.timedelta(hours=1))
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        db_sess.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data, duration=datetime.timedelta(hours=1))
            return redirect("/")
        return render_template(
            'login.html',
            message="Неправильный логин или пароль",
            form=form
        )
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
def index():
    db_sess = create_session()
    works = db_sess.query(Jobs).all()
    users = db_sess.query(User).all()
    team_leaders = {}
    for worker in works:
        for user in users:
            if worker.team_leader == user.id:
                team_leaders[worker.team_leader] = user.surname + ' ' + user.name
    updated_works = [{
        'id': work.id, 'job': work.job, 'leader': team_leaders[work.team_leader],
        'duration': work.end_date - work.start_date, 'collaborators': work.collaborators,
        'is_finished': work.is_finished
    } for work in works]
    db_sess.close()
    return render_template('magazine.html', works={'works': updated_works})


if __name__ == '__main__':
    email = None
    global_init('db/database.db')
    app.run(host='127.0.0.1', port=5000)
