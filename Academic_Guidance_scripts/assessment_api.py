import os
import logging
import traceback
from flask import Flask, jsonify, request
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('assessment_api')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add file handler
log_file = Path(__file__).parent / "api.log"
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.info("🚀 Starting UMP Career Guidance API")

# Initialize Firebase
try:
    logger.info("Initializing Firebase...")
    current_dir = Path(__file__).parent
    key_path = current_dir / "serviceAccountKey.json"
    
    if not key_path.exists():
        logger.critical(f"Service account file not found at: {key_path}")
        raise FileNotFoundError(f"Service account file not found at {key_path}")
    
    cred = credentials.Certificate(str(key_path))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("✅ Firebase initialized successfully")
    
    # Test connection
    test_ref = db.collection('connection_test').document('api_start')
    test_ref.set({'timestamp': datetime.utcnow().isoformat()})
    logger.info("🔥 Firestore connection test successful")
    
except Exception as e:
    logger.critical(f"Firebase init failed: {e}")
    logger.critical(traceback.format_exc())
    raise SystemExit("Firebase initialization failed")

def get_matching_courses(interests):
    """Fetch all UMP courses and filter based on interests"""
    try:
        logger.info(f"Fetching courses matching interests: {interests}")
        # Get all faculty documents
        faculties_ref = db.collection('ump_courses')
        faculties = faculties_ref.stream()
        
        undergrad_courses = []
        postgrad_courses = []
        course_count = 0
        
        for faculty_doc in faculties:
            faculty_data = faculty_doc.to_dict()
            faculty_name = faculty_data['faculty']
            
            # Process each school in the faculty
            for school in faculty_data.get('schools', []):
                school_name = school['name']
                
                # Process undergraduate courses
                for course in school.get('undergraduate', []):
                    course_interests = course.get('related_interests', [])
                    if any(interest in course_interests for interest in interests):
                        undergrad_courses.append({
                            'name': course['name'],
                            'faculty': faculty_name,
                            'school': school_name,
                            'level': 'undergraduate',
                            'match_score': calculate_match_score(interests, course_interests)
                        })
                        course_count += 1
                
                # Process postgraduate courses
                for course in school.get('postgraduate', []):
                    course_interests = course.get('related_interests', [])
                    if any(interest in course_interests for interest in interests):
                        postgrad_courses.append({
                            'name': course['name'],
                            'faculty': faculty_name,
                            'school': school_name,
                            'level': 'postgraduate',
                            'match_score': calculate_match_score(interests, course_interests)
                        })
                        course_count += 1
        
        logger.info(f"Found {len(undergrad_courses)} undergrad and {len(postgrad_courses)} postgrad courses")
        return undergrad_courses, postgrad_courses
        
    except Exception as e:
        logger.error(f"Error fetching courses: {str(e)}")
        logger.error(traceback.format_exc())
        return [], []

def calculate_match_score(user_interests, item_interests):
    """Calculate match score percentage"""
    if not user_interests or not item_interests:
        return 0
    
    common = set(user_interests) & set(item_interests)
    score = round((len(common) / len(user_interests)) * 100, 2)
    return score

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
        interests = data.get('interests', [])
        logger.info(f"Received recommendation request for interests: {interests}")
        
        if not interests:
            logger.warning("No interests provided for recommendations")
            return jsonify({
                'success': True,
                'careers': [],
                'undergrad_courses': [],
                'postgrad_courses': []
            })
        
        # Get recommended careers
        careers_ref = db.collection('careers')
        careers = []
        career_ids = set()  # Track seen career IDs to avoid duplicates
        
        for interest in interests:
            logger.debug(f"Querying careers for interest: {interest}")
            query = careers_ref.where('related_interests', 'array_contains', interest)
            docs = query.stream()
            
            for doc in docs:
                if doc.id in career_ids:
                    continue
                    
                career_ids.add(doc.id)
                career = doc.to_dict()
                career['id'] = doc.id
                career_interests = career.get('related_interests', [])
                career['match_score'] = calculate_match_score(interests, career_interests)
                careers.append(career)
        
        logger.info(f"Found {len(careers)} careers matching interests")
        
        # Get recommended UMP courses
        undergrad, postgrad = get_matching_courses(interests)
        
        # Sort by match score (descending)
        careers.sort(key=lambda x: x['match_score'], reverse=True)
        undergrad.sort(key=lambda x: x['match_score'], reverse=True)
        postgrad.sort(key=lambda x: x['match_score'], reverse=True)
        
        response = {
            'success': True,
            'careers': careers,
            'undergrad_courses': undergrad,
            'postgrad_courses': postgrad
        }
        
        logger.info(f"Returning {len(careers)} careers, {len(undergrad)} undergrad, {len(postgrad)} postgrad courses")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Recommendations error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/assessment/<assessment_id>', methods=['GET'])
def get_assessment(assessment_id):
    try:
        logger.info(f"Fetching assessment: {assessment_id}")
        doc_ref = db.collection('assessments').document(assessment_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            logger.warning(f"Assessment not found: {assessment_id}")
            return jsonify({
                'success': False,
                'error': 'Assessment not found'
            }), 404
        
        assessment = doc.to_dict()
        logger.info(f"Found assessment: {assessment_id}")
        return jsonify({
            'success': True,
            'assessment': assessment
        })
        
    except Exception as e:
        logger.error(f"Get assessment error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/assessment/latest/<user_id>', methods=['GET'])
def get_latest_assessment(user_id):
    try:
        logger.info(f"Fetching latest assessment for user: {user_id}")
        assessments_ref = db.collection('assessments')
        query = assessments_ref.where('user_id', '==', user_id)\
                              .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                              .limit(1)
        docs = query.stream()
        latest_doc = next(docs, None)

        if not latest_doc:
            logger.warning(f"No assessments found for user: {user_id}")
            return jsonify({'success': False, 'error': 'No assessment found'}), 404

        assessment = latest_doc.to_dict()
        logger.info(f"Found latest assessment for user {user_id}: {latest_doc.id}")
        return jsonify({
            'success': True,
            'assessment': assessment,
            'id': latest_doc.id
        })
    except Exception as e:
        logger.error(f"Error fetching latest assessment: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/assessments', methods=['POST'])
def create_assessment():
    try:
        data = request.get_json()
        logger.info("Creating new assessment")
        
        # Add timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = firestore.SERVER_TIMESTAMP
            
        new_doc_ref = db.collection('assessments').document()
        new_doc_ref.set(data)
        
        logger.info(f"Created assessment: {new_doc_ref.id}")
        return jsonify({
            'success': True,
            'id': new_doc_ref.id
        }), 201
        
    except Exception as e:
        logger.error(f"Error saving assessment: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/assessments', methods=['GET'])
def get_all_assessments():
    try:
        logger.info("Fetching all assessments")
        assessments_ref = db.collection('assessments')
        docs = assessments_ref.stream()
        assessments_list = []
        
        for doc in docs:
            assessment = doc.to_dict()
            assessment['id'] = doc.id
            assessments_list.append(assessment)
        
        logger.info(f"Found {len(assessments_list)} assessments")
        return jsonify({
            'success': True,
            'assessments': assessments_list
        })
    except Exception as e:
        logger.error(f"Error fetching assessments: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Health check received")
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'ump-career-guidance-api'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)