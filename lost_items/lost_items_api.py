from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import uuid
import os
import json
import firebase_admin
from firebase_admin import credentials, auth
import re
from sqlalchemy import or_
from flask import send_from_directory



# Initialize Flask app
app = Flask(__name__)
CORS(
    app,
    resources={ r"/*": {"origins": "*"} },      # <-- all routes, all origins
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# Configure database
####################################    make sure to replace with your mysql workbench details
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Brilliant2004@localhost:3306/sccs_lf'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Initialize Firebase
if not firebase_admin._apps:
    firebase_json = os.environ["FIREBASE_SERVICE_ACCOUNT"]
    cred_dict     = json.loads(firebase_json)
    cred          = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)


# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Model
class LostItem(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(128), nullable=False)
    item_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(255), nullable=False)

    date_lost = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    contact_info = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_name': self.item_name,
            'description': self.description,
            'category': self.category,
            'date_lost': self.date_lost.isoformat(),
            'location': self.location,
            'contact_info': self.contact_info,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat()
        }

@app.route('/api/report-item', methods=['POST'])
def report_item():
    # Verify Firebase token
    id_token = request.headers.get('Authorization')
    if not id_token:
        return jsonify({'error': 'Authorization token missing'}), 401

    try:
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
    except Exception as e:
        return jsonify({'error': 'Invalid authentication token'}), 401

    # Validate and save image
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No selected image file'}), 400

    # Generate unique filename
    file_ext = os.path.splitext(image_file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(save_path)

    # Create new LostItem entry
    try:
        new_item = LostItem(
            id=str(uuid.uuid4()),
            user_id=user_id,
            item_name=request.form['itemName'],
            description=request.form['description'],
            category=request.form['category'],
            date_lost=datetime.strptime(request.form['dateLost'], '%Y-%m-%d'),
            location=request.form['location'],
            contact_info=request.form['contactInfo'],
            image_path=filename
        )

        db.session.add(new_item)
        db.session.commit()
        return jsonify(new_item.serialize()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@app.route('/api/fetch-items', methods=['POST'])
def fetch_items():
    # 1. Verify Firebase token
    id_token = request.headers.get('Authorization')
    if not id_token:
        return jsonify({'error': 'Authorization token missing'}), 401

    try:
        decoded = auth.verify_id_token(id_token)
        user_id = decoded['uid']
    except Exception:
        return jsonify({'error': 'Invalid authentication token'}), 401

    # 2. Parse and validate request body
    data = request.get_json() or {}
    categories = data.get('categories')     # now a list of full strings + words
    if not isinstance(categories, list) or not categories:
        return jsonify({'error': 'Must provide a non-empty list of categories'}), 400

    # Build an OR-filter for *every* category term
    filters = []
    for term in categories:
        clean = term.strip().lower()
        if not clean:
            continue
        # match anywhere in the category column
        filters.append(LostItem.category.ilike(f'%{clean}%'))

    if not filters:
        return jsonify({'error': 'No valid search terms'}), 400

    try:
        # Query any item whose `category` matches *any* of your terms
        items = LostItem.query.filter(or_(*filters)).distinct().all()
        return jsonify([itm.serialize() for itm in items]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/fetch-all-items', methods=['GET'])
def fetch_all_items():
    try:
        items = LostItem.query.order_by(LostItem.created_at.desc()).all()
        return jsonify([item.serialize() for item in items]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Add this endpoint for debugging
@app.route('/api/healthcheck')
def healthcheck():
    return jsonify({"status": "ok", "database": "connected"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
