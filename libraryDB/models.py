from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum as PgEnum, Table
from flask import Flask, request, jsonify, g, abort, send_file, url_for
from flask_cors import CORS
from datetime import datetime, date, time, timedelta, timezone
import uuid
import os
import firebase_admin
from firebase_admin import credentials, auth, db as firebase_db
from sqlalchemy import func, and_, or_
from werkzeug.exceptions import NotFound, Unauthorized, Forbidden
from werkzeug.utils import secure_filename
from flask import send_from_directory
from sqlalchemy.exc import SQLAlchemyError
import traceback
from sqlalchemy.dialects.mysql import LONGBLOB
import base64

app = Flask(__name__)
# CORS config allowing Authorization header
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Authorization", "Content-Type"]
)

# --- Configuration ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL env var is required")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret-key')

basedir = os.path.dirname(os.path.abspath(__file__))
app.config.setdefault('MEDIA_UPLOAD_FOLDER', os.path.join(basedir, 'uploads', 'media'))
os.makedirs(app.config['MEDIA_UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# --- Initialize Firebase once ---
if not firebase_admin._apps:
    firebase_path = os.path.join(basedir, 'sccs-a27f7-firebase-adminsdk-fbsvc-9286791118.json')
    firebase_cred = credentials.Certificate(firebase_path)
    firebase_admin.initialize_app(firebase_cred, {
        'databaseURL': 'https://sccs-a27f7-default-rtdb.firebaseio.com/'
    })

# --- Models ---

# User model with reflection for existing table
with app.app_context():
    user_table = Table(
        'user',
        db.metadata,
        autoload_with=db.engine,
        extend_existing=True
    )

class User(db.Model):
    __table__ = user_table
    
    # Relationships from both files
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    loans = db.relationship('Loan', backref='user', lazy=True)
    fees = db.relationship('FeeFine', backref='user', lazy=True)
    appointments = db.relationship('Appointment', foreign_keys='Appointment.user_id', backref='user', lazy=True)
    purchase_requests = db.relationship('PurchaseRequest', backref='user', lazy=True)
    recommendations = db.relationship('Recommendation', backref='user', lazy=True)
    study_memberships = db.relationship('StudyRoomMember', backref='user', lazy='dynamic')
    media_uploads = db.relationship('StudyRoomMedia', backref='user', lazy='dynamic')

class Library(db.Model):
    __tablename__ = 'library'
    library_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    location = db.Column(db.String(256), nullable=False)
    type = db.Column(db.String(64), nullable=False, default='Information Center')
    
    # Relationships
    operating_hours = db.relationship('OperatingTime', backref='library', lazy=True)

class OperatingTime(db.Model):
    __tablename__ = 'operatingtime'
    operating_time_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    library_id = db.Column(db.Integer, db.ForeignKey('library.library_id'), nullable=False)
    weekday = db.Column(db.Enum('Mon','Tue','Wed','Thu','Fri','Sat','Sun'), nullable=False)
    open_time = db.Column(db.Time, nullable=False)
    close_time = db.Column(db.Time, nullable=False)

class Room(db.Model):
    __tablename__ = 'room'
    room_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    library_id = db.Column(db.Integer, db.ForeignKey('library.library_id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    room_type = db.Column(db.String(20), nullable=False) 
    seats = db.relationship('Seat', backref='room', lazy=True)

class Seat(db.Model):
    __tablename__ = 'seat'
    seat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False)
    identifier = db.Column(db.String(64), nullable=False)
    is_computer = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_occupied = db.Column(db.Boolean, default=False)
    specs = db.Column(db.String(256), default='Standard specs')

class StudyRoom(db.Model):
    __tablename__ = 'study_room'
    room_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(100))
    capacity = db.Column(db.Integer, default=10)
    created_by = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class StudyRoomMember(db.Model):
    __tablename__ = 'study_room_member'
    member_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('study_room.room_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    student_number = db.Column(db.String(50))
    student_email = db.Column(db.String(255))
    status = db.Column(db.Enum('pending','approved','rejected'), default='pending')
    joined_at = db.Column(db.DateTime)

class StudyRoomMedia(db.Model):
    __tablename__ = 'study_room_media'
    media_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('study_room.room_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    file_name = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    file_path = db.Column(db.String(512))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudyRoomMindMap(db.Model):
    __tablename__ = 'study_room_mindmap'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('study_room.room_id'), unique=True)
    data = db.Column(db.JSON)  # Stores nodes and connections

class Book(db.Model):
    __tablename__ = 'book'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(32), unique=True, nullable=False)
    title = db.Column(db.String(512), nullable=False)
    author = db.Column(db.String(256), nullable=False)
    publisher = db.Column(db.String(256))
    year = db.Column(db.Integer)
    copies_total = db.Column(db.Integer, default=1)
    copies_available = db.Column(db.Integer, default=1)
    image = db.Column(LONGBLOB, nullable=True)  
    
    # Relationships
    reservations = db.relationship('Reservation', backref='book', lazy=True)
    loans = db.relationship('Loan', backref='book', lazy=True)

class Reservation(db.Model):
    __tablename__ = 'reservation'
    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    library_id = db.Column(db.Integer, db.ForeignKey('library.library_id'), nullable=False)
    reserved_from = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reserved_until = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('active', 'cancelled', 'fulfilled'), default='active')

class Loan(db.Model):
    __tablename__ = 'loan'
    loan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    checkout_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    returned_date = db.Column(db.Date)

class FeeFine(db.Model):
    __tablename__ = 'feefine'
    feefine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    amount = db.Column(db.Numeric(8,2), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum('unpaid', 'paid'), default='unpaid')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Announcement(db.Model):
    __tablename__ = 'announcement'
    announcement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text, nullable=False)
    posted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Appointment(db.Model):
    __tablename__ = 'appointment'
    appointment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    librarian_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    library_id = db.Column(db.Integer, db.ForeignKey('library.library_id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('pending','confirmed','cancelled','completed'), default='pending')
    notes = db.Column(db.Text)

    # Relationships
    librarian = db.relationship('User', foreign_keys=[librarian_user_id])

class PurchaseRequest(db.Model):
    __tablename__ = 'purchaserequest'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    title = db.Column(db.String(512), nullable=False)
    author = db.Column(db.String(256), nullable=False)
    isbn = db.Column(db.String(32))
    justification = db.Column(db.Text)
    status = db.Column(db.Enum('open','ordered','declined','received'), default='open')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    __tablename__ = 'recommendation'
    rec_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    category = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('new','reviewed','implemented','rejected'), default='new')

# Create tables and seed initial data
with app.app_context():
    db.create_all()

    if Library.query.count() == 0:
        default_libraries = [
            {
                "name": "Thoko Mayekiso",
                "location": "Mbombela Mian campus",
                "type": "Information Center"
            }
        ]

        for lib_def in default_libraries:
            db.session.add(Library(**lib_def))

        db.session.commit()
        print("🌱 Seeded default libraries")
    else:
        print(f"✅ {Library.query.count()} libraries already present, skipping seed")

def initialize_library(library_id=1):
    # Create default rooms if they don't exist
    rooms = [
        {"name": "library-lab01", "type": "computer_lab"},
        {"name": "library-lab02", "type": "computer_lab"},
        {"name": "library-lab03", "type": "computer_lab"},
        {"name": "library-lab04", "type": "computer_lab"},
        {"name": "studyarea", "type": "study_room"},
    ]
    
    for room_data in rooms:
        room = Room.query.filter_by(
            library_id=library_id,
            name=room_data["name"]
        ).first()
        
        if not room:
            room = Room(
                library_id=library_id,
                name=room_data["name"],
                room_type=room_data["type"]
            )
            db.session.add(room)
            db.session.commit()
            
            # Create seats for this room
            seat_count = 50 if "lab" in room_data["name"] else 100
            prefix = "Slab" if "lab" in room_data["name"] else "SSlib-"
            
            for i in range(1, seat_count + 1):
                identifier = f"{prefix}{i:02d}" if "lab" in room_data["name"] else f"{prefix}{i}"
                
                seat = Seat(
                    room_id=room.room_id,
                    identifier=identifier,
                    is_computer=("lab" in room_data["name"]),
                    is_active=True,
                    is_occupied=False
                )
                db.session.add(seat)
    
    db.session.commit()
