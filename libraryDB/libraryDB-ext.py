from flask import Flask, request, jsonify, g, abort, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import uuid, os, json
import firebase_admin
from firebase_admin import credentials, auth, db as firebase_db
from sqlalchemy import Table
from werkzeug.exceptions import NotFound, Unauthorized, Forbidden
from werkzeug.utils import secure_filename
from flask import send_from_directory
from libraryDB.lIbraryDB import db, User

app = Flask(__name__)
# CORS config allowing Authorization header
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Authorization", "Content-Type"]
)

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL env var is required")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']                 = os.getenv('JWT_SECRET', 'super-secret-key')

basedir = os.path.dirname(os.path.abspath(__file__))
app.config.setdefault('MEDIA_UPLOAD_FOLDER', os.path.join(basedir, 'uploads', 'media'))
os.makedirs(app.config['MEDIA_UPLOAD_FOLDER'], exist_ok=True)

# --- Initialize Firebase once ---
if not firebase_admin._apps:
    # Pull the JSON from env var
    firebase_json = os.environ["FIREBASE_SERVICE_ACCOUNT"]
    cred_dict     = json.loads(firebase_json)
    # Use it to create the credential
    cred          = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://sccs-a27f7-default-rtdb.firebaseio.com/'
    })



# --- Authentication Middleware ---
PUBLIC_ENDPOINTS = {'register_user', 'static', 'favicon'}

@app.before_request
def authenticate_request():
    print("→ Incoming", request.method, request.path, "Auth:",
          request.headers.get('Authorization'))
    if request.method == 'OPTIONS' or request.endpoint in PUBLIC_ENDPOINTS:
        return

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise Unauthorized('Missing or invalid Authorization header')
    token = auth_header.split(' ', 1)[1]
    try:
        decoded = auth.verify_id_token(token)
        request.firebase_uid = decoded['uid']
        user = User.query.filter_by(firebase_uid=request.firebase_uid).first()
        if not user:
            raise NotFound('User not found')
        g.current_user = user
    except Exception as e:
        import traceback
        print("‼️ Token verification failed:", e)
        traceback.print_exc()
        raise Unauthorized(f'Invalid token: {e}')

# --- Models ---
class OperatingTime(db.Model):
    __tablename__ = 'operatingtime'
    operating_time_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    library_id        = db.Column(db.Integer, db.ForeignKey('library.library_id'), nullable=False)
    weekday           = db.Column(db.Enum('Mon','Tue','Wed','Thu','Fri','Sat','Sun', name='weekday_enum'), nullable=False)
    open_time         = db.Column(db.Time, nullable=False)
    close_time        = db.Column(db.Time, nullable=False)

class Library(db.Model):
    __tablename__ = 'library'
    library_id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name           = db.Column(db.String(256), nullable=False)
    location       = db.Column(db.String(256), nullable=False)
    type           = db.Column(db.String(64), nullable=False, default='Information Center')
    # relationship defined after both classes

class StudyRoom(db.Model):
    __tablename__ = 'study_room'
    room_id        = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(255), nullable=False)
    description    = db.Column(db.Text)
    subject        = db.Column(db.String(100))
    capacity       = db.Column(db.Integer, default=10)
    created_by     = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    is_active      = db.Column(db.Boolean, default=True)

class StudyRoomMember(db.Model):
    __tablename__ = 'study_room_member'
    member_id      = db.Column(db.Integer, primary_key=True)
    room_id        = db.Column(db.Integer, db.ForeignKey('study_room.room_id'))
    user_id        = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    student_number = db.Column(db.String(50))
    student_email  = db.Column(db.String(255))
    status         = db.Column(db.Enum('pending','approved','rejected',name='membership_status_enum'), default='pending')
    joined_at      = db.Column(db.DateTime)

    # ← ADD THIS:
    user = db.relationship(
        'User',
        backref=db.backref('study_memberships', lazy='dynamic'),
        lazy='joined'
    )


class StudyRoomMedia(db.Model):
    __tablename__ = 'study_room_media'
    media_id       = db.Column(db.Integer, primary_key=True)
    room_id        = db.Column(db.Integer, db.ForeignKey('study_room.room_id'))
    user_id        = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    file_name      = db.Column(db.String(255))
    file_type      = db.Column(db.String(50))
    file_path      = db.Column(db.String(512))
    uploaded_at    = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship(
        'User',
        backref=db.backref('media_uploads', lazy='dynamic'),
        lazy='joined'
    )

class StudyRoomMindMap(db.Model):
    __tablename__ = 'study_room_mindmap'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('study_room.room_id'), unique=True)
    data = db.Column(db.JSON)  # Stores nodes and connections

# define relationship after both sides are known
Library.operating_hours = db.relationship('OperatingTime', backref='library', lazy=True)


# 7. Chat Messages
@app.route('/libraries/<int:library_id>/chat/messages', methods=['GET', 'POST'])
def chat_messages(library_id):
    ref = firebase_db.reference(f'chats/{library_id}/messages')
    
    if request.method == 'GET':
        # Get last 50 messages
        messages = ref.order_by_child('timestamp').limit_to_last(50).get() or {}
        return jsonify(list(messages.values()))
    
    elif request.method == 'POST':
        data = request.get_json()
        msg_id = str(uuid.uuid4())
        
        payload = {
            'user_id': request.current_user.user_id,
            'name': request.current_user.name,
            'text': data['text'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        ref.child(msg_id).set(payload)
        return jsonify(payload), 201

# 15. User Registration (Sync with Firebase)
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    firebase_uid = data.get('firebase_uid')
    
    if not firebase_uid:
        return jsonify({'error': 'Firebase UID required'}), 400
    
    # Check if user exists
    existing = User.query.filter_by(firebase_uid=firebase_uid).first()
    if existing:
        return jsonify({'user_id': existing.user_id}), 200
    
    # Create new user
    user = User(
        firebase_uid=firebase_uid,
        name=data['name'],
        email=data['email'],
        role=data.get('role', 'student')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'user_id': user.user_id,
        'name': user.name,
        'email': user.email
    }), 201

# --- Study Room Endpoints ---

# Create study room
@app.route('/study_rooms', methods=['POST'])
def create_study_room():
    data = request.get_json()
    new_room = StudyRoom(
        name=data['name'],
        description=data['description'],
        subject=data['subject'],
        capacity=data['capacity'],
        created_by=g.current_user.user_id
    )
    db.session.add(new_room)
    db.session.flush()   # so new_room.room_id is populated

    # Auto‑approve the creator:
    owner_membership = StudyRoomMember(
        room_id=new_room.room_id,
        user_id=g.current_user.user_id,
        student_number=None,      # optional
        student_email=None,       # optional
        status='approved',
        joined_at=datetime.utcnow()
    )
    db.session.add(owner_membership)

    db.session.commit()
    return jsonify({
        'room_id': new_room.room_id,
        'name': new_room.name,
        'created_at': new_room.created_at.isoformat()
    }), 201


# List study rooms
@app.route('/study_rooms', methods=['GET'])
def list_study_rooms():
    rooms = StudyRoom.query.filter_by(is_active=True).all()
    return jsonify([{
        'room_id': r.room_id,
        'name': r.name,
        'description': r.description,
        'subject': r.subject,
        'capacity': r.capacity,
        'created_by': r.created_by,
        'created_at': r.created_at.isoformat(),
        'member_count': StudyRoomMember.query.filter_by(room_id=r.room_id, status='approved').count()
    } for r in rooms])


# Join request with university details
@app.route('/study_rooms/<int:room_id>/join', methods=['POST'])
def request_join_room(room_id):
    data = request.get_json() or {}

    # allow either snake_case or camelCase
    student_number = data.get('student_number') or data.get('studentNumber')
    student_email  = data.get('student_email')  or data.get('studentEmail')

      # DEBUG: show exactly what arrived
    print("💾 /join payload keys:", list(data.keys()))
    student_number = data.get('student_number') or data.get('studentNumber')
    student_email  = data.get('student_email')  or data.get('studentEmail')
    print("💾 student_number:", repr(student_number))
    print("💾 student_email: ", repr(student_email))

    if not student_number or not student_email:
        return jsonify({
            'error': 'Both student_number (or studentNumber) and student_email (or studentEmail) are required'
        }), 400



    room = StudyRoom.query.get_or_404(room_id)
    existing = StudyRoomMember.query.filter_by(
        room_id=room_id,
        user_id=g.current_user.user_id
    ).first()
    if existing:
        return jsonify({'message': 'Join request already exists'}), 400

    new_request = StudyRoomMember(
        room_id=room_id,
        user_id=g.current_user.user_id,
        student_number=student_number,
        student_email=student_email,
        status='pending'
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Join request submitted'}), 201

@app.route('/study_rooms/<int:room_id>', methods=['GET'])
def get_study_room(room_id):
    room = StudyRoom.query.get_or_404(room_id)
    
    # Check if current user is approved member
    membership = StudyRoomMember.query.filter_by(
        room_id=room_id,
        user_id=g.current_user.user_id,
        status='approved'
    ).first()
    
    if not membership:
        abort(403, description="You must be an approved member to access this room")
    
    return jsonify({
        'room_id': room.room_id,
        'name': room.name,
        'description': room.description,
        'subject': room.subject,
        'capacity': room.capacity,
        'created_by': room.created_by,
        'created_at': room.created_at.isoformat(),
        'is_creator': room.created_by == g.current_user.user_id
    })


# list_pending_requests endpoint
@app.route('/study_rooms/<int:room_id>/members/pending', methods=['GET'])
def list_pending_requests(room_id):
    # Verify room owner
    room = StudyRoom.query.filter_by(
        room_id=room_id,
        created_by=g.current_user.user_id
    ).first()
    
    if not room:
        abort(404, description="Room not found or you're not the creator")
    
    # Get pending requests
    pending = StudyRoomMember.query.filter_by(
        room_id=room_id,
        status='pending'
    ).all()
    
    return jsonify([{
        'user_id': m.user_id,
        'name': m.user.name,
        'student_number': m.student_number,
        'student_email': m.student_email,
        'joined_at': m.joined_at.isoformat() if m.joined_at else None
    } for m in pending])

# List room members
@app.route('/study_rooms/<int:room_id>/members', methods=['GET'])
def list_room_members(room_id):
    # Verify user is approved member
    membership = StudyRoomMember.query.filter_by(
        room_id=room_id,
        user_id=g.current_user.user_id,
        status='approved'
    ).first()
    if not membership:
        abort(403, description="You must be an approved member to view members")
    
    members = StudyRoomMember.query.filter_by(room_id=room_id, status='approved').all()
    return jsonify([{
        'user_id': m.user_id,
        'name': m.user.name,
        'student_number': m.student_number,
        'student_email': m.student_email,
        'joined_at': m.joined_at.isoformat() if m.joined_at else None
    } for m in members])

# Approve/reject members
@app.route('/study_rooms/<int:room_id>/members/<int:user_id>', methods=['PUT'])
def update_member_status(room_id, user_id):
    # Verify room owner
    room = StudyRoom.query.filter_by(
        room_id=room_id,
        created_by=g.current_user.user_id
    ).first_or_404()
    
    member = StudyRoomMember.query.filter_by(
        room_id=room_id,
        user_id=user_id
    ).first_or_404()
    
    data = request.get_json()
    member.status = data['status']
    if data['status'] == 'approved':
        member.joined_at = datetime.utcnow()
        
    db.session.commit()
    return jsonify({'message': 'Member status updated'})

@app.route('/study_rooms/<int:room_id>/membership', methods=['GET'])
def get_membership_status(room_id):

    """
    Returns the current user’s membership info for this room:
      - status: 'pending', 'approved', 'rejected', or 'not_member'
      - user_id:    so the front‑end can test `room.created_by === user_id`
      - student_number & student_email: for display if approved
    """
    m = StudyRoomMember.query.filter_by(
        room_id=room_id,
        user_id=g.current_user.user_id
    ).first()

    if not m:
        return jsonify({'status': 'not_member'}), 200

    return jsonify({
        'user_id':        m.user_id,
        'status':         m.status,
        'student_number': m.student_number,
        'student_email':  m.student_email
    }), 200



# Upload media to room
UPLOAD_FOLDER = 'uploads/study_rooms'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png', 'mp4', 'mov', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# media upload 
@app.route('/media/<filename>')
def serve_media(filename):
    return send_from_directory(app.config['MEDIA_UPLOAD_FOLDER'], filename)
@app.route('/study_rooms/<int:room_id>/media', methods=['POST'])
def upload_media(room_id):
    # 1. Verify user is an approved member (your existing logic)
    membership = StudyRoomMember.query.filter_by(
        room_id=room_id,
        user_id=g.current_user.user_id,
        status='approved'
    ).first_or_404()

    # 2. Get file from form-data
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 3. Generate a UUID filename + keep extension
    ext      = os.path.splitext(file.filename)[1]
    uid_name = f"{uuid.uuid4().hex}{ext}"
    safe_name= secure_filename(uid_name)

    # 4. Save to disk
    save_path = os.path.join(app.config['MEDIA_UPLOAD_FOLDER'], safe_name)
    file.save(save_path)

    # 5. Persist in DB
    media = StudyRoomMedia(
        room_id=   room_id,
        user_id=   g.current_user.user_id,
        file_name= safe_name,
        file_type= file.mimetype,
        file_path= save_path
    )
    db.session.add(media)
    db.session.commit()

    # 6. Return the new record (including a URL)
    return jsonify({
        'media_id':   media.media_id,
        'file_name':  media.file_name,
        'file_type':  media.file_type,
        'uploaded_at': media.uploaded_at.isoformat(),
        'url':        url_for('serve_media', filename=media.file_name, _external=True)
    }), 201

# List room media
@app.route('/study_rooms/<int:room_id>/media', methods=['GET'])
def list_room_media(room_id):
    # Verify user is approved member
    membership = StudyRoomMember.query.filter_by(
        room_id=room_id,
        user_id=g.current_user.user_id,
        status='approved'
    ).first_or_404()
    
    media_list = StudyRoomMedia.query.filter_by(room_id=room_id).all()
    return jsonify([{
        'media_id': m.media_id,
        'file_name': m.file_name,
        'file_type': m.file_type,
        'uploaded_at': m.uploaded_at.isoformat(),
        'user_id': m.user_id,
        'user_name': m.user.name
    } for m in media_list])

# Download media
@app.route('/media/<int:media_id>', methods=['GET'])
def download_media(media_id):
    media = StudyRoomMedia.query.get_or_404(media_id)
    
    # Verify user is approved member of the room
    membership = StudyRoomMember.query.filter_by(
        room_id=media.room_id,
        user_id=g.current_user.user_id,
        status='approved'
    ).first()
    if not membership:
        abort(403, description="You are not authorized to download this file")
    
    return send_file(media.file_path, as_attachment=True)


# To do list endpoint 
@app.route('/study_rooms/<int:room_id>/mindmap', methods=['GET', 'POST'])
def room_mindmap(room_id):
    # Check user is approved member
    membership = StudyRoomMember.query.filter_by(
        room_id=room_id,
        user_id=g.current_user.user_id,
        status='approved'
    ).first()
    if not membership:
        abort(403, description="You must be an approved member to access this mindmap")
    
    if request.method == 'GET':
        mindmap = StudyRoomMindMap.query.filter_by(room_id=room_id).first()
        if mindmap:
            return jsonify(mindmap.data)
        return jsonify({'nodes': [], 'connections': []}), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        mindmap = StudyRoomMindMap.query.filter_by(room_id=room_id).first()
        
        if mindmap:
            mindmap.data = data
        else:
            mindmap = StudyRoomMindMap(room_id=room_id, data=data)
            db.session.add(mindmap)
        
        db.session.commit()
        return jsonify({'message': 'Mindmap saved'}), 200


# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Authentication required'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

if __name__ == '__main__':
    with app.app_context():
        app.run(host='0.0.0.0', port=5006, debug=True)
