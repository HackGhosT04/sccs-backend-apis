import os
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)



# Load SendGrid API key from environment
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
if not SENDGRID_API_KEY:
    raise RuntimeError("Please set the SENDGRID_API_KEY environment variable")

# In‐memory store (demo only—swap for Redis/db in production)
verification_codes = {}

@app.route("/send-code", methods=["POST"])
def send_verification_code():
    data = request.json or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Generate 6-digit code
    code = str(random.randint(100000, 999999))
    verification_codes[email] = code

    # Build the email
    message = Mail(
        from_email="230252427@ump.ac.za",  
        to_emails=email,
        subject="Your SCCS Verification Code",
        html_content=f"<p>Your verification code is: <strong>{code}</strong></p>"
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        # You can inspect response.status_code or response.body if needed
        return jsonify({"message": "Verification code sent"}), 200
  
    except Exception as e:
        # Log full exception on the server console:
        print("=== SendGrid Error ===")
        print(e)
        # If it’s a SendGrid exception, it may have a .body or .status_code attribute:
        try:
            body = e.body.decode() if hasattr(e, "body") else str(e)
        except:
            body = str(e)
        return (
            jsonify({
              "error": "Failed to send email",
              "details": body
            }),
            500
        )

@app.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.json or {}
    email = data.get("email")
    code = data.get("code")
    if verification_codes.get(email) == code:
        # Optionally delete the code so it can't be reused:
        verification_codes.pop(email, None)
        return jsonify({"verified": True}), 200
    return jsonify({"verified": False, "error": "Invalid code"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
