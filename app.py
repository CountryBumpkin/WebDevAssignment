import os
from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User
from routes import product_routes
from auth import auth_routes

app = Flask(__name__)

# secret key 
app.config['SECRET_KEY'] = 'your_secret_key_here'

# database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "jacks_healthy_food_shop.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# uploads folder configuration
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# initialises db
db.init_app(app)

# initialises login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_routes.login"

# user loader for login manager
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# register blueprints
app.register_blueprint(product_routes)
app.register_blueprint(auth_routes)

# homepage route
@app.route('/')
def home():
    return render_template('index.html')

# runs flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
