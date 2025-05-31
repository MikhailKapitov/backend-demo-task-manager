import os
import jwt
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from eureka_client import init_eureka
from db import db, init_db, is_token_revoked, revoke_token, cleanup_revoked_tokens


load_dotenv()

app = Flask(__name__)

init_db(app)

SERVICE_NAME = "jwt-service"
PORT = 8083
init_eureka(SERVICE_NAME, PORT)

ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET', 'default-access-secret')
REFRESH_TOKEN_SECRET = os.getenv('REFRESH_TOKEN_SECRET', 'default-refresh-secret')
ACCESS_TOKEN_EXPIRATION = 900  # 15 minutes.
REFRESH_TOKEN_EXPIRATION = 1209600  # 14 days.

print(ACCESS_TOKEN_SECRET, REFRESH_TOKEN_SECRET)

def create_jti():
    return str(uuid.uuid4())

def create_token(login, token_type, secret, expiration):
    jti = create_jti()
    expires = datetime.utcnow() + timedelta(seconds=expiration)
    payload = {
        'login': login,
        'exp': expires,
        'jti': jti,
        'type': token_type
    }
    return jwt.encode(payload, secret, algorithm='HS256'), jti, expires

@app.route('/api/token/create', methods=['POST'])
def create_token_pair():
    data = request.json
    if not data or 'login' not in data:
        return jsonify({"error": "Missing login"}), 400
    
    login = data['login']
    
    access_token, access_jti, access_exp = create_token(
        login, 'access', ACCESS_TOKEN_SECRET, ACCESS_TOKEN_EXPIRATION
    )
    refresh_token, refresh_jti, refresh_exp = create_token(
        login, 'refresh', REFRESH_TOKEN_SECRET, REFRESH_TOKEN_EXPIRATION
    )
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_jti": access_jti,
        "refresh_jti": refresh_jti
    })

@app.route('/api/token/refresh', methods=['POST'])
def refresh_access_token():
    data = request.json
    if not data or 'refresh_token' not in data:
        return jsonify({"error": "Missing refresh token"}), 400
    
    try:
        payload = jwt.decode(
            data['refresh_token'], 
            REFRESH_TOKEN_SECRET, 
            algorithms=['HS256']
        )
        
        if payload.get('type') != 'refresh':
            return jsonify({"error": "Invalid token type"}), 401
        
        if is_token_revoked(payload['jti']):
            return jsonify({"error": "Token revoked"}), 401
            
        access_token, access_jti, access_exp = create_token(
            payload['login'], 'access', ACCESS_TOKEN_SECRET, ACCESS_TOKEN_EXPIRATION
        )
        
        return jsonify({
            "access_token": access_token,
            "access_jti": access_jti
        })
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401

@app.route('/api/token/verify', methods=['POST'])
def verify_token():
    data = request.json
    if not data or 'token' not in data:
        return jsonify({"error": "Missing token"}), 400
    
    try:
        token = data['token']
        try:
            payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=['HS256'])
            if payload.get('type') != 'access':
                return jsonify({"error": "Invalid token type"}), 401
        except jwt.InvalidTokenError:
            payload = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=['HS256'])
            if payload.get('type') != 'refresh':
                return jsonify({"error": "Invalid token type"}), 401
        
        if is_token_revoked(payload['jti']):
            return jsonify({"error": "Token revoked"}), 401
            
        return jsonify({"valid": True, "login": payload['login']}), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
