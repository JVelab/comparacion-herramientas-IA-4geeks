from flask import Blueprint, jsonify, g
from extensions import db
from models import User
from utils import success_response, jwt_required


protected_bp = Blueprint("protected", __name__)


@protected_bp.route("/me", methods=["GET"])
@jwt_required
def get_current_user():
    user = db.session.get(User, g.user_id)

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify(success_response("User retrieved", {"user": user.to_dict()})), 200


@protected_bp.route("/protected", methods=["GET"])
@jwt_required
def protected_route():
    return jsonify(success_response("This is a protected route", {
        "user_id": g.user_id
    })), 200