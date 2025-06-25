from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

#Retrieving react app host name
react_host= os.getenv("FLASK_FRONTEND_HOST_NAME")
#Retrieving secret key
secretKey= os.getenv("FLASK_SECRET_KEY")

#Handling Cross Origin Requests
CORS(app, origins=[react_host], supports_credentials=True)

app.secret_key = secretKey

# app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

# For storing the Users
USERS = {}
# For storing the generated tokens
TOKENS = {}

@app.route('/auth/send-magic-link', methods=['POST'])
def sendMagicLink():
    #Extract the email and tenant associated with the request
    data = request.json
    email = data['email']
    tenant = data['tenantId']

    print("react_host", react_host)
    print("secret key", secretKey)
    # Return error if the email and tenantID fields are empty
    if not email or not tenant:
        return jsonify({'error': 'Missing fields'}), 400
    
    # Save user or Associating the user with their tenant
    USERS[email] = {'tenantId': tenant}

    # Generate token using UUID
    token = str(uuid.uuid4())
    TOKENS[token] = {
        'email': email,
        'tenantId': tenant,
        'expires_at': datetime.now() + timedelta(minutes=30)
    }

    # Simulate email by logging magic link
    print(f"Magic link is {react_host}/auth/callback?token={token}")
    return jsonify({'message': 'Magic link sent!'}), 200

@app.route('/auth/callback')
def auth_callback():
    
    token = request.args.get('token') #extracting the token from parameters
    token_data = TOKENS.get(token) #Getting the user data corresponding to the token viz. email, tenantID and expiry
    
    #Error when token_data is not available
    if not token_data:
        return jsonify({'error': 'Invalid or expired token'}), 400

    #Error when token has expired
    if token_data['expires_at'] < datetime.now():
        return jsonify({'error': 'Token expired'}), 401

    #Start a session for the user & saving the corresponding email and tenantId
    session['email'] = token_data['email']
    session['tenantId'] = token_data['tenantId']

    return jsonify({'message': 'Redirection to Dashboard'}), 200

@app.route('/api/snippet')
def get_snippet():
    #Checking if the session exists
    if 'email' not in session or 'tenantId' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    #Verifying user belongs to a valid tenant as having an active session
    js = session['tenantId']   
    if not js:
        return jsonify({'error': 'Tenant not found'}), 404

    #Returning Dynamic tenantId as per the user
    return jsonify({'script': js})

# starting the backend
if __name__ == '__main__':
    app.run(port=5000, debug=True)