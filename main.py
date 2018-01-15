from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '123abc!'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text(256))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user'] = username
            return redirect('/new_post')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():      
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']          
        if username == '' or len(username) < 3 or ' ' in username:      
            flash('A username containing at least three characters and no spaces is required', 'error')
            return render_template('signup.html')  
        if password == '' or len(password) < 3 or ' ' in password:      
            flash('A password containing at least three characters and no spaces is required', 'error')
            return render_template('signup.html')
        if verify != password:
            flash("Passwords must match", 'error')
            return render_template('signup.html')
        else:
            existing_user = User.query.filter_by(username=username).first()          
            if existing_user:
                    flash('Username already used', 'error')          
            else:    
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/new_post')              
    return render_template('signup.html')

@app.route('/new_post', methods=['POST', 'GET'])
def new_post():
    if request.method == 'GET':
        return render_template('new_post.html')
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username = session['user']).first()
        post = Blog(title=title, body=body, owner=owner)
        id = post.id
        if len(title) == 0 or len(body) == 0:
            flash('Please fill in both title and body', 'error')
            return render_template('new_post')      
        if len(title) > 0 and len(body) > 0:          
            blog = Blog(title, body, owner)
            blog_id = request.args.get('id')
            blog = Blog.query.get(blog_id)
            return render_template('single_post.html', blog=blog)

@app.route('/blog', methods = ['POST', 'GET'])
def blog():    
    if request.args.get('user'):
        user_id = request.args.get('user')
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner=user).all()
        return render_template('single_user.html', blogs=blogs)
    elif  request.args.get('id'):
        blog_id = (request.args.get('id'))
        blog = Blog.query.get(blog_id)
        user_id = (request.args.get('id'))
        user = User.query.filter_by(id=user_id)
        return render_template('single_post.html', blog=blog) 
    else: 
        blogs = Blog.query.all()
        writer_id = (request.args.get('writer_id'))
        user = User.query.filter_by(id=writer_id)
        return render_template('blog.html', blogs=blogs, user=user)

@app.route('/')
def index():
    all_users = User.query.all()
    return render_template('index.html', all_users = all_users)

@app.route('/logout')
def logout():
    if 'username' in session:  
        del session['username']
        return redirect('/')
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run()
