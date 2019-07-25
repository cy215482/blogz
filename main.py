from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



app = Flask(__name__)
app.secret_key = "923hr2nc';l,"
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:passwordlol@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

some_engine = create_engine('mysql+pymysql://blogz:passwordlol@localhost:8889/blogz')
Session = sessionmaker(bind=some_engine)

# create a Session
session = Session()


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    content = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True)
    body = db.Column(db.Text)
    password = db.Column(db.String(120))

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog_listing']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def blog_listing():
    title = "Blogz"

    if session:
        owner = User.query.filter_by(username = session['username']).first()

    if "id" in request.args:
        post_id = request.args.get('id')
        blog = Blog.query.filter_by(id = post_id).all()
        return render_template('blogs.html', title = title, Blog = Blog, post_id = post_id)

    elif "user" in request.args:
        user_id = request.args.get('user')
        blog = Blog.query.filter_by(owner_id = user_id).all()
        return render_template('blogs.html', title = title, Blog = Blog)

    else:
        blog = Blog.query.order_by(Blog.id.desc()).all()
        return render_template('blogs.html', title = title, Blog = Blog)

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = ""
    username_error = ""
    password_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()

        if not user:
            username_error = "User does not exist."
            return redirect ('/login')
            if username == "":
                username_error = "Please enter your username."
                return redirect ('/signup')

        if password == "":
            password_error = "Please enter your password."
            return redirect('/login')
   
        if user and user.password != password:
            password_error = "That is the wrong password."

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

    return render_template('login.html', username = username, username_error = username_error, password_error = password_error)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = ""
    username_error = ""
    password_error = ""
    verify_error = ""

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username = username).first()

        if len(username) < 3:
            username_error = "Usernames must be longer than 3 characters."
            if username == "":
                username_error = "Please enter a username."
      
        if password != verify:
            password_error = "Passwords must match."
            verify_error = "Passwords must match."
            
        if len(password) < 3:
            password_error = "Password must be longer than 3 characters."
            if password == "":
                password_error = "Please enter a valid password."

        if password != verify:
            password_error = "Passwords must match."
            verify_error = "Passwords must match."

        if not username_error and not password_error and not verify_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                username_error = "Username is already claimed."

    return render_template('signup.html', username = username, username_error = username_error, password_error = password_error, verify_error = verify_error)

@app.route('/newpost', methods=['POST', 'GET'])
def create_new_post():
    blog_title = ""
    blog_content = ""
    title_error = ""
    content_error = ""
    owner = User.query.filter_by(username = session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_content = request.form['blog_content']

        if blog_title == "":
            title_error = "Please enter a title!"

        if blog_content == "":
            content_error = "Please enter a post!"

        if title_error == "" and content_error == "":
            new_post = Blog(blog_title, blog_content, owner)
            db.session.add(new_post)
            db.session.commit()
            blog_id = Blog.query.order_by(Blog.id.desc()).first()
            user = owner

            return redirect('/blog?id={}&user={}'.format(blog_id.id, user.username))

    return render_template('newpost.html', title = "Add a new post", blog_title = blog_title, blog_content = blog_content, title_error = title_error, content_error = content_error)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == "__main__":

    app.run()