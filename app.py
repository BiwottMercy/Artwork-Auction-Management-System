from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artwork_auction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Artwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    starting_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, default=0.0)
    is_sold = db.Column(db.Boolean, default=False)

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artwork.id'), nullable=False)
    bid_amount = db.Column(db.Float, nullable=False)

# Routes

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Artwork Auction Backend!"})

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        role=data['role']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful!", "user_id": user.id, "role": user.role})
    return jsonify({"error": "Invalid email or password"}), 401

# List Artworks
@app.route('/artworks', methods=['GET'])
def get_artworks():
    artworks = Artwork.query.all()
    return jsonify([{
        "id": artwork.id,
        "title": artwork.title,
        "description": artwork.description,
        "artist_id": artwork.artist_id,
        "starting_price": artwork.starting_price,
        "current_price": artwork.current_price,
        "is_sold": artwork.is_sold
    } for artwork in artworks])

# Add Artwork
@app.route('/artworks', methods=['POST'])
def add_artwork():
    data = request.get_json()
    new_artwork = Artwork(
        title=data['title'],
        description=data['description'],
        artist_id=data['artist_id'],
        starting_price=data['starting_price']
    )
    db.session.add(new_artwork)
    db.session.commit()
    return jsonify({"message": "Artwork added successfully!"}), 201

# Place a Bid
@app.route('/bids', methods=['POST'])
def place_bid():
    data = request.get_json()
    artwork = Artwork.query.get(data['artwork_id'])
    if artwork.is_sold:
        return jsonify({"error": "Artwork is already sold"}), 400
    if data['bid_amount'] <= artwork.current_price:
        return jsonify({"error": "Bid must be higher than the current price"}), 400

    new_bid = Bid(user_id=data['user_id'], artwork_id=data['artwork_id'], bid_amount=data['bid_amount'])
    artwork.current_price = data['bid_amount']
    db.session.add(new_bid)
    db.session.commit()
    return jsonify({"message": "Bid placed successfully!"})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)