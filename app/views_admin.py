import os
from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from .extensions import db
from .models import User
from .auth import admin_required

bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')

@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    try:
        users = User.query.all()
        # Don't send password hashes back!
        user_list = [{"id": u.id, "username": u.username, "role": u.role} for u in users]
        return jsonify(user_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    try:
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password_hash=hashed, role=role)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500