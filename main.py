from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, PasswordField, validators
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret_key'

# Replace YOUR_USERNAME and YOUR_PASS

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = '[YOUR_USERNAME]'
app.config['MYSQL_PASSWORD'] = '[YOU_PASS]'
app.config['MYSQL_DB'] = 'todo_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please login', 'danger')
            return redirect(url_for('login'))

    return wrap


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# Login Form Class
class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])


# Home
@app.route('/')
@is_logged_in
def home():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM todos WHERE user_id = %s", [session['user_id']])
    todos = cur.fetchall()
    cur.close()
    return render_template('index.html', todos=todos)


# Register User
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
                    (name, email, username, password))
        mysql.connection.commit()
        cur.close()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_candidate = form.password.data

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['user_id'] = data['id']
                session['username'] = data['username']

                flash('You are now logged in', 'success')
                return redirect(url_for('home'))
            else:
                error = 'Invalid login'
                return render_template('login.html', form=form, error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', form=form, error=error)

    return render_template('login.html', form=form)


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# Add Todo
@app.route('/add_todo', methods=['POST'])
@is_logged_in
def add_todo():
    task = request.form['task']
    description = request.form['description']
    user_id = session['user_id']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO todos(task, description, user_id) VALUES(%s, %s, %s)", (task, description, user_id))
    mysql.connection.commit()
    cur.close()

    flash('Todo Added', 'success')
    return redirect(url_for('home'))


# Delete Todo
@app.route('/delete_todo/<string:id>', methods=['POST'])
@is_logged_in
def delete_todo(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()

    flash('Todo Deleted', 'success')
    return redirect(url_for('home'))


def create_database():
    cursor = mysql.connection.cursor()

    # Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS todo_db")

    # Switch to the database
    cursor.execute("USE todo_db")

    # Create the 'users' table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            username VARCHAR(25) NOT NULL,
            password VARCHAR(100) NOT NULL,
            PRIMARY KEY (id),
            UNIQUE (username)
        )
    """)

    # Create the 'todos' table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INT NOT NULL AUTO_INCREMENT,
            task VARCHAR(255) NOT NULL,
            description TEXT,
            completed BOOLEAN NOT NULL DEFAULT 0,
            user_id INT NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    mysql.connection.commit()
    cursor.close()


if __name__ == '__main__':
    app.run(debug=True)
