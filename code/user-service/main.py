import os
import uuid
import requests
from flask import Flask, request, jsonify
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from db import db, User
from eureka_client import init_eureka
import py_eureka_client.eureka_client as eureka_client


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
ph = PasswordHasher()

SERVICE_NAME = "user-service"
PORT = 8082
init_eureka(SERVICE_NAME, PORT)


# Useful for testing.
def drop_db():
    db.drop_all()
    db.create_all()

def get_jwt_service_url():
    
    client = eureka_client.get_client()
    app = client.applications.get_application("jwt-service")
    
    up_instances = app.up_instances

    
    if up_instances:
        instance = up_instances[0]
        # print(instance.port.port, dir(instance.port.port))
        app_url = f"http://{instance.ipAddr}:{instance.port.port}"
        return app_url
    
    return None

def create_tokens(login):

    # Placeholder for testing.
    # return {"refresh_token": "refresh_token_goes_here", "access_token": "access_token_goes_here"}
    
    jwt_url = f"{get_jwt_service_url()}/api/token/create"
    response = requests.post(jwt_url, json={"login": login})
    if response.status_code == 200:
        return {"access_token": response.json()["access_token"], "refresh_token": response.json()["refresh_token"]}
    return None

def verify_token(token):

    # Placeholder for testing.
    # return True

    jwt_url = f"{get_jwt_service_url()}/api/token/verify"
    response = requests.post(jwt_url, json={"token": token})
    return response.status_code == 200

def get_token_login(token):

    # Placeholder for testing.
    # return "username_goes_here"

    jwt_url = f"{get_jwt_service_url()}/api/token/verify"
    response = requests.post(jwt_url, json={"token": token})
    if response.status_code != 200:
        return None
    return response.json().get("login")

@app.route('/api/user/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'login' not in data or 'password' not in data:
        return jsonify({"error": "Missing login or password"}), 400
    
    if User.query.filter_by(login=data['login']).first():
        return jsonify({"error": "User already exists"}), 409
        
    password_hash = ph.hash(data['password'])
    new_user = User(
        id=str(uuid.uuid4()),
        login=data['login'],
        password_hash=password_hash
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    tokens = create_tokens(data['login'])
    return jsonify({"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]}), 201

@app.route('/api/user/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'login' not in data or 'password' not in data:
        return jsonify({"error": "Missing login or password"}), 400
    
    user = User.query.filter_by(login=data['login']).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
        
    try:
        ph.verify(user.password_hash, data['password'])
    except VerifyMismatchError:
        return jsonify({"error": "Invalid credentials"}), 401
    
    tokens = create_tokens(data['login'])
    return jsonify({"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]})

@app.route('/api/user', methods=['DELETE'])
def delete_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing token"}), 401
        
    token = auth_header.split(" ")[1]
    if not verify_token(token):
        return jsonify({"error": "Invalid token"}), 401
        
    login = get_token_login(token)
    if not login:
        return jsonify({"error": "Login required"}), 400
        
    user = User.query.filter_by(login=login).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200

if __name__ == '__main__':
    with app.app_context():
        drop_db()
        db.create_all()
    app.run(host='0.0.0.0', port=PORT)
