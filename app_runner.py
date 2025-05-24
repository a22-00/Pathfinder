import sys
import os

project_root = os.path.abspath(os.path.dirname(__file__))

# Debug prints
print(f"DEBUG: Value of __file__ is: {__file__}")
print(f"DEBUG: Calculated project_root is: {project_root}")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"DEBUG: Added to sys.path: {project_root}")
else:
    print(f"DEBUG: Already in sys.path: {project_root}")

print("DEBUG: Current sys.path (after modification):")
for i, p in enumerate(sys.path):
    print(f"  [{i}] - {p}")

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

from project_learn_track.routes.main import main_bp
from project_learn_track.routes.auth import auth_bp
from project_learn_track.routes.api import api_bp
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev_default_secret_key_123!@#')
app.config['MY_ENDPOINT_API_KEY'] = os.getenv('MY_ENDPOINT_API_KEY', 'default-secret-dev-key-if-not-set')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
CORS(app)

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Pathfinder API!'})

@app.route('/my-endpoint')
def my_endpoint():
    key = request.args.get('api_key')
    INTERNAL_API_KEY_FOR_MY_ENDPOINT = app.config.get('MY_ENDPOINT_API_KEY', "default-secret-dev-key-if-not-set")
    if key != INTERNAL_API_KEY_FOR_MY_ENDPOINT:
        return jsonify({'error': 'Unauthorized for my-endpoint'}), 401
    return jsonify({'message': 'Success accessing my-endpoint!'})

app.register_blueprint(main_bp, url_prefix='/app')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(api_bp, url_prefix='/api/v1')

if __name__ == '__main__':
    is_debug_mode = app.config.get('DEBUG', False)
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(debug=is_debug_mode, port=port, host='0.0.0.0')

from flask import render_template
from flask import send_from_directory

@app.route('/pathfinder')
def serve_pathfinder_html():
    return send_from_directory(os.path.join(project_root, 'static'), 'Pathfinder.html')

@app.route('/')
def home_html():
    return render_template('Pathfinder.html')