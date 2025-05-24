# File: project_learn_track/routes/api.py
from flask import Blueprint, request, jsonify
# from ..services import content_generator_service # etc.

api_bp = Blueprint('api_routes', __name__)

@api_bp.route('/content/generate', methods=['POST'])
def api_generate_content():
    data = request.json
    topic = data.get('topic')
    print(f"API ROUTE: Generating content for topic '{topic}'") # Placeholder
    content = f"API-Generated study sheet for {topic}"
    return jsonify({"topic": topic, "generated_content": content}), 200
