from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import credentials, firestore, initialize_app, auth
import firebase_admin
import os
import traceback
import logging
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('academic_planning_api')

# Initialize Firebase
try:
    logger.info("Initializing Firebase...")
    current_dir = Path(__file__).parent
    key_path = current_dir / "serviceAccountKey.json"
    logger.info(f"Looking for service account at: {key_path}")
    
    if not key_path.exists():
        logger.critical(f"Service account file not found at: {key_path}")
        raise FileNotFoundError(f"Service account file not found at {key_path}")
    
    cred = credentials.Certificate(str(key_path))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("✅ Firebase initialized")
    
    # Test connection
    test_ref = db.collection('connection_test').document('academic_init')
    test_ref.set({'timestamp': datetime.utcnow().isoformat()})
    logger.info("✅ Firestore connection test successful")
except Exception as e:
    logger.critical(f"Firebase init failed: {str(e)}")
    logger.critical(traceback.format_exc())
    raise SystemExit("Firebase initialization failed")

def verify_token(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return None, "Missing or invalid Authorization header"
        
        id_token = auth_header.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token, None
    except Exception as e:
        return None, f"Token verification failed: {str(e)}"

# Career Endpoints
@app.route('/api/careers', methods=['GET'])
def get_careers():
    try:
        careers_ref = db.collection('careers')
        docs = careers_ref.stream()
        
        careers = []
        for doc in docs:
            career_data = doc.to_dict()
            careers.append({
                'id': doc.id,
                'title': career_data.get('title', ''),
                'description': career_data.get('description', ''),
                'personality_traits': career_data.get('personality_traits', []),
                'interests': career_data.get('interests', []),
                'values': career_data.get('values', []),
                'faculty': career_data.get('faculty', ''),
                'roadmap': career_data.get('roadmap', [])
            })
        
        return jsonify({"success": True, "careers": careers})
    except Exception as e:
        logger.error(f"Get careers error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/careers/<career_id>', methods=['GET'])
def get_career(career_id):
    try:
        career_ref = db.collection('careers').document(career_id)
        career_doc = career_ref.get()
        
        if not career_doc.exists:
            return jsonify({"success": False, "error": "Career not found"}), 404
            
        career_data = career_doc.to_dict()
        
        # Get roadmap if available
        roadmap = []
        if 'roadmap' in career_data:
            roadmap = career_data['roadmap']
        elif 'roadmap_ref' in career_data:
            # Handle roadmap as subcollection reference
            roadmap_ref = career_ref.collection('roadmap')
            roadmap_docs = roadmap_ref.stream()
            for doc in roadmap_docs:
                roadmap.append(doc.to_dict())
        
        # Get related courses
        courses = []
        if 'suggested_courses' in career_data:
            courses_ref = db.collection('ump_courses')
            for course_id in career_data['suggested_courses']:
                course_doc = courses_ref.document(course_id).get()
                if course_doc.exists:
                    courses.append(course_doc.to_dict())
        
        # Get postgraduate programs
        postgraduate = []
        if 'postgraduate' in career_data:
            pg_ref = db.collection('ump_courses')
            for pg_id in career_data['postgraduate']:
                pg_doc = pg_ref.document(pg_id).get()
                if pg_doc.exists:
                    postgraduate.append(pg_doc.to_dict())
        
        return jsonify({
            "success": True,
            "career": {
                "id": career_doc.id,
                "title": career_data.get('title', ''),
                "description": career_data.get('description', ''),
                "personality_traits": career_data.get('personality_traits', []),
                "interests": career_data.get('interests', []),
                "values": career_data.get('values', []),
                "faculty": career_data.get('faculty', ''),
                "roadmap": roadmap,
                "suggested_courses": courses,
                "postgraduate": postgraduate
            }
        })
    except Exception as e:
        logger.error(f"Get career error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

# UMP Courses Endpoint
@app.route('/api/ump-courses', methods=['GET'])
def get_ump_courses():
    try:
        ump_ref = db.collection('ump_courses')
        docs = ump_ref.stream()
        
        courses = []
        for doc in docs:
            course_data = doc.to_dict()
            courses.append({
                'id': doc.id,
                'name': course_data.get('name', ''),
                'description': course_data.get('description', ''),
                'faculty': course_data.get('faculty', ''),
                'school': course_data.get('school', ''),
                'duration': course_data.get('duration', ''),
                'requirements': course_data.get('requirements', ''),
                'careers': course_data.get('careers', [])
            })
        
        return jsonify({"success": True, "ump_courses": courses})
    except Exception as e:
        logger.error(f"Get UMP courses error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Academic Plan Endpoints
@app.route('/api/academic-plans', methods=['POST'])
def save_academic_plan():
    try:
        decoded_token, error = verify_token(request)
        if error:
            return jsonify({"success": False, "error": error}), 401
            
        user_id = decoded_token['uid']
        data = request.get_json()
        
        if not data or 'careerGoal' not in data or 'degreeProgram' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400
        
        plan_data = {
            'userId': user_id,
            'careerGoal': data['careerGoal'],
            'degreeProgram': data['degreeProgram'],
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Create or update plan
        plan_ref = db.collection('academic_plans').document(user_id)
        plan_ref.set(plan_data, merge=True)
        
        return jsonify({
            "success": True,
            "message": "Academic plan saved"
        })
    except Exception as e:
        logger.error(f"Save academic plan error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/academic-plans', methods=['GET'])
def get_academic_plan():
    try:
        decoded_token, error = verify_token(request)
        if error:
            return jsonify({"success": False, "error": error}), 401
            
        user_id = decoded_token['uid']
        plan_ref = db.collection('academic_plans').document(user_id)
        plan = plan_ref.get()
        
        if plan.exists:
            return jsonify({
                "success": True,
                "academicPlan": plan.to_dict()
            })
        else:
            return jsonify({
                "success": True,
                "academicPlan": {
                    "careerGoal": "",
                    "degreeProgram": ""
                }
            })
    except Exception as e:
        logger.error(f"Get academic plan error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Learning Modules Endpoints
@app.route('/api/learning-modules', methods=['POST'])
def save_learning_modules():
    try:
        decoded_token, error = verify_token(request)
        if error:
            return jsonify({"success": False, "error": error}), 401
            
        user_id = decoded_token['uid']
        data = request.get_json()
        
        if not data or 'years' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: years"
            }), 400
            
        # Validate structure
        if not isinstance(data['years'], list):
            return jsonify({
                "success": False,
                "error": "Years must be an array"
            }), 400
            
        modules_data = {
            'years': data['years'],
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Create or update modules
        modules_ref = db.collection('learning_modules').document(user_id)
        modules_ref.set(modules_data, merge=True)
        
        return jsonify({
            "success": True,
            "message": "Learning modules saved"
        })
    except Exception as e:
        logger.error(f"Save learning modules error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/learning-modules', methods=['GET'])
def get_learning_modules():
    try:
        decoded_token, error = verify_token(request)
        if error:
            return jsonify({"success": False, "error": error}), 401
            
        user_id = decoded_token['uid']
        modules_ref = db.collection('learning_modules').document(user_id)
        modules = modules_ref.get()
        
        if modules.exists:
            return jsonify({
                "success": True,
                "learningModules": modules.to_dict()
            })
        else:
            return jsonify({
                "success": True,
                "learningModules": {"years": []}
            })
    except Exception as e:
        logger.error(f"Get learning modules error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Timetable Endpoints
@app.route('/api/timetables', methods=['POST'])
def save_timetable():
    try:
        decoded_token, error = verify_token(request)
        if error:
            return jsonify({"success": False, "error": error}), 401
            
        user_id = decoded_token['uid']
        data = request.get_json()
        
        if not data or 'blocks' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: blocks"
            }), 400
            
        # Validate structure
        if not isinstance(data['blocks'], list):
            return jsonify({
                "success": False,
                "error": "Blocks must be an array"
            }), 400
            
        timetable_data = {
            'blocks': data['blocks'],
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Create or update timetable
        timetable_ref = db.collection('timetables').document(user_id)
        timetable_ref.set(timetable_data, merge=True)
        
        return jsonify({
            "success": True,
            "message": "Timetable saved"
        })
    except Exception as e:
        logger.error(f"Save timetable error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/timetables', methods=['GET'])
def get_timetable():
    try:
        decoded_token, error = verify_token(request)
        if error:
            return jsonify({"success": False, "error": error}), 401
            
        user_id = decoded_token['uid']
        timetable_ref = db.collection('timetables').document(user_id)
        timetable = timetable_ref.get()
        
        if timetable.exists:
            return jsonify({
                "success": True,
                "timetable": timetable.to_dict()
            })
        else:
            return jsonify({
                "success": True,
                "timetable": {"blocks": []}
            })
    except Exception as e:
        logger.error(f"Get timetable error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Career Plan Endpoints
@app.route('/api/career-plans', methods=['POST'])
def save_career_plan():
    try:
        decoded_token, error = verify_token(request)
        if error:
            return jsonify({"success": False, "error": error}), 401
            
        user_id = decoded_token['uid']
        data = request.get_json()
        
        if not data or 'careerId' not in data or 'content' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400
        
        plan_data = {
            'userId': user_id,
            'careerId': data['careerId'],
            'content': data['content'],
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Create or update career plan
        plan_ref = db.collection('career_plans').document(user_id)
        plan_ref.set(plan_data, merge=True)
        
        return jsonify({
            "success": True,
            "message": "Career plan saved"
        })
    except Exception as e:
        logger.error(f"Save career plan error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/career-plans', methods=['GET'])
def get_career_plan():
    try:
        decoded_token, error = verify_token(request)
        if error:
            return jsonify({"success": False, "error": error}), 401
            
        user_id = decoded_token['uid']
        plan_ref = db.collection('career_plans').document(user_id)
        plan = plan_ref.get()
        
        if plan.exists:
            plan_data = plan.to_dict()
            # Get career details
            career_data = {}
            if 'careerId' in plan_data:
                career_ref = db.collection('careers').document(plan_data['careerId'])
                career_doc = career_ref.get()
                if career_doc.exists:
                    career_data = career_doc.to_dict()
            
            return jsonify({
                "success": True,
                "careerPlan": {
                    "id": plan.id,
                    "careerId": plan_data.get('careerId', ''),
                    "careerTitle": career_data.get('title', ''),
                    "content": plan_data.get('content', ''),
                    "updatedAt": plan_data.get('updatedAt', '').isoformat() if 'updatedAt' in plan_data else ''
                }
            })
        else:
            return jsonify({
                "success": True,
                "careerPlan": {
                    "careerId": "",
                    "content": ""
                }
            })
    except Exception as e:
        logger.error(f"Get career plan error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "firebase": "connected" if firebase_admin._apps else "disconnected",
        "version": "1.1.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)