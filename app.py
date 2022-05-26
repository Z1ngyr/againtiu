# https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3-ru
# Импорт сторонних модулей
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

# Создание flask приложения в объекте app
app = Flask(__name__)
# Создание секретного ключа для исключения кибератаки MITM "man in the middle" или "человек посередине", погуглите про нее
app.config['SECRET_KEY'] = 'your secret key'


# Функция для создания подключения к БД
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Функция для получения одного поста из БД, либо возврата страницы Not found (код 404)
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


# Привязка маршрута / к функции index на GET запрос
@app.route('/')
# Функция для получения данных для главной страницы и ее отрисовки из шаблона
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


# Привязка маршрута /целое_число к функции post на GET запрос
@app.route('/<int:post_id>')
# Функция для получения данных для конкретного поста и его отрисовки из шаблона
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


# Привязка маршрута /create к функции create на POST и GET запрос
@app.route('/create', methods=('GET', 'POST'))
# Функция для отрисовки шаблона создания поста, а также обработки отправки нового поста на сервер и его сохранения
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Необходим заголовок!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


# Привязка маршрута /целое_число/edit к функции edit на POST и GET запрос
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
# Функция для отрисовки шаблона редактирования поста, а также обработки отправки изменений поста на сервер и его сохранения
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Необходим заголовок!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


# Привязка маршрута /целое_число/delete к функции delete на POST запрос
@app.route('/<int:id>/delete', methods=('POST',))
# Функция для удаления поста
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" был успешно удален!'.format(post['title']))
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')
