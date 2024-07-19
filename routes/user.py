import os
import base64
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import true
from model.model import db, Predict, Feedback, User
from werkzeug.security import generate_password_hash
from utils.predict import CLASS_NAMES, MODEL, read_file_as_image, np

bp = Blueprint('user', __name__)


@bp.route('/getUser')
@jwt_required()
def getUserDetails():
    user = get_jwt_identity()
    return jsonify(user)


@bp.route('/updateUser', methods=['PUT'])
@jwt_required()
def update_user_details():
    user_identity = get_jwt_identity()
    user = User.query.filter_by(id=user_identity['id']).first()

    if not user:
        return jsonify(message="User not found"), 404

    data = request.json

    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify(message="Missing fields"), 400

    user.username = username
    user.email = email

    try:
        db.session.commit()
        return jsonify(message="User details updated successfully"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Error updating user details: {str(e)}"), 500


@bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    users = User.query.all()
    if not users:
        return jsonify(message="No users found"), 404

    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

    return jsonify(users=user_list), 200


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify(message="User not found"), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify(message="User deleted successfully"), 200


@bp.route("/getFeedback", methods=["POST"])
def feedback():
    data = request.json
    print(data["form"]["feedback"])
    feedback = data["form"]["feedback"]

    print(
        f"Received data: feedback={feedback}")

    if not feedback:
        return jsonify({"error": "Missing fields"}), 400

    new_feedback = Feedback(feedback=feedback)

    try:
        db.session.add(new_feedback)
        db.session.commit()
        print("User added to database")
        return jsonify({"message": "Successfull"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding feedback to database: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route('/feedback', methods=['GET'])
@jwt_required()
def get_all_feedback():
    feedback_list = Feedback.query.all()
    if not feedback_list:
        return jsonify(message="No feedback found"), 404

    feedback_data = []
    for feedback in feedback_list:
        feedback_data.append({
            "id": feedback.id,
            "feedback": feedback.feedback,
        })

    return jsonify(feedback=feedback_data), 200


@bp.route('/prediction/history')
@jwt_required()
def history():
    user = get_jwt_identity()
    predicts = Predict.query.filter_by(user_id=user['id']).all()

    if not predicts:
        return jsonify(message="No history found yet"), 404

    list_predict = []
    for predict in predicts:
        list_predict.append({
            "id": predict.id,
            "img_path": predict.img_path,
            "disease_type": predict.disease_type,
            "confidence_accuracy": predict.confidence_accuracy,
        })

    return jsonify(history=list_predict)


@bp.route('/prediction/history/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_history(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify(message="User not found"), 404

    predicts = Predict.query.filter_by(user_id=user.id).all()
    if not predicts:
        return jsonify(message="No history found"), 404

    list_predict = []
    for predict in predicts:
        list_predict.append({
            "id": predict.id,
            "img_path": predict.img_path,
            "disease_type": predict.disease_type,
            "confidence_accuracy": predict.confidence_accuracy,
        })

    return jsonify(history=list_predict), 200


@bp.route('/prediction/history/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_history_item(id):
    user = get_jwt_identity()
    predict = Predict.query.filter_by(id=id, user_id=user['id']).first()

    if not predict:
        return jsonify(message="Item not found"), 404

    try:
        db.session.delete(predict)
        db.session.commit()
        return jsonify(message="Item deleted successfully"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(message="Failed to delete item", error=str(e)), 500


@bp.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    user = get_jwt_identity()
    try:
        data = request.json
        image_base64 = data.get('base64')
        file_name = data.get('fileName')

        if not image_base64 or not file_name:
            return jsonify({"error": "No image data or filename provided"}), 400

        image_data = base64.b64decode(image_base64)
        image_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], file_name)

        with open(image_path, 'wb') as f:
            f.write(image_data)

        image = read_file_as_image(image_path)
        img_batch = np.expand_dims(image, 0)
        prediction = MODEL.predict(img_batch)

        predicted_class = CLASS_NAMES[np.argmax(prediction[0])]
        confidence = np.max(prediction[0])

        prediction = Predict(user_id=user['id'], img_path=file_name,
                             disease_type=predicted_class, confidence_accuracy=float(confidence))

        db.session.add(prediction)
        db.session.commit()

        prediction_result = {
            "img_path": prediction.img_path,
            "disease_type": prediction.disease_type,
            "confidence_accuracy": prediction.confidence_accuracy,
        }

        return jsonify({
            "message": "Image received and saved",
            "result": prediction_result
        }), 201

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
