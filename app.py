from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model with hashed password storage
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Function to initialize the database
def init_db():
    # Create all tables defined in the SQLAlchemy models
    db.create_all()

# Routes for user registration, login, logout, and serving the frontend
@app.route('/register', methods=['POST'])
def register():
    if request.method != 'POST':
        return jsonify({'error': 'Method Not Allowed'}), 405
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Basic input validation
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Check for existing user
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400

    # Create new user with hashed password
    new_user = User()
    new_user.username = username
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    if request.method != 'POST':
        return jsonify({'error': 'Method Not Allowed'}), 405

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Check for existing user and verify password
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Implement session management (replace with desired mechanism)
    session['user_id'] = user.id

    return jsonify({'message': 'Login successful'})

@app.route('/logout', methods=['GET'])
def logout():
    if request.method != 'GET':
        return jsonify({'error': 'Method Not Allowed'}), 405

    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'})

# Route to handle GET requests for the root URL
@app.route('/', methods=['GET'])
def index():
    if request.method != 'GET':
        return jsonify({'error': 'Method Not Allowed'}), 405
    
    return app.send_static_file('index.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '404 Not Found'}), 404

# Call the init_db function when the application starts
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
