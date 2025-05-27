import logging
from pythonjsonlogger import jsonlogger
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from prometheus_flask_exporter import PrometheusMetrics
import os

app = Flask(__name__)

# Fetch environment variables
mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/playlists_db')
if not mongo_uri:
    raise ValueError("Environment variable MONGODB_URI is not set or empty. Please set it appropriately.")

app.config["MONGO_URI"] = mongo_uri

# Initialize PyMongo with retry logic
try:
    mongo = PyMongo(app)
    # Test connection
    mongo.db.command('ping')
    print(f"Connected to MongoDB successfully")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    print("Make sure MongoDB is running and accessible")

metrics = PrometheusMetrics(app)

# Configure logging to output JSON format
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
app.logger.addHandler(logHandler)
app.logger.setLevel(logging.DEBUG)

# Define loggers for each endpoint
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def get_landing():
    app.logger.debug('GET request received on landing endpoint')
    # return render_template('index.html')
    return jsonify({"service": "Playlists API", "version": "1.0"})


@app.route('/playlists/<name>', methods=['POST'])
def add_playlist(name):
    app.logger.debug(f'POST request received on add_playlist endpoint for name: {name}')
    
    if not request.is_json:
        return jsonify(error="Request must contain valid JSON"), 400
    
    try:
        playlist = request.json
        if not playlist:
            return jsonify(error="Empty JSON data"), 400
            
        playlist['name'] = name
        
        # Check if playlist already exists
        existing = mongo.db.playlists.find_one({'name': name})
        if existing:
            return jsonify(error="Playlist already exists"), 409
            
        result = mongo.db.playlists.insert_one(playlist)
        app.logger.info(f'Playlist created: {name}')
        return jsonify(
            message="Playlist added successfully", 
            name=name,
            id=str(result.inserted_id)
        ), 201
        
    except Exception as e:
        app.logger.error(f'Error creating playlist: {str(e)}')
        return jsonify(error=f"Failed to create playlist: {str(e)}"), 500

@app.route('/playlists/<name>', methods=['PUT'])
def update_playlist(name):
    app.logger.debug(f'PUT request received on update_playlist endpoint for name: {name}')
    
    if not request.is_json:
        return jsonify(error="Request must contain valid JSON"), 400
    
    try:
        playlist = request.json
        if not playlist:
            return jsonify(error="Empty JSON data"), 400
            
        # Don't allow changing the name
        playlist.pop('name', None)
        
        result = mongo.db.playlists.update_one({'name': name}, {'$set': playlist})
        if result.matched_count == 0:
            return jsonify(error="Playlist not found"), 404
            
        app.logger.info(f'Playlist updated: {name}')
        return jsonify(message="Playlist updated"), 200
        
    except Exception as e:
        app.logger.error(f'Error updating playlist: {str(e)}')
        return jsonify(error=f"Failed to update playlist: {str(e)}"), 500

@app.route('/playlists/<name>', methods=['DELETE'])
def delete_playlist(name):
    app.logger.debug(f'DELETE request received on delete_playlist endpoint for name: {name}')
    
    try:
        result = mongo.db.playlists.delete_one({'name': name})
        if result.deleted_count == 0:
            return jsonify(error="Playlist not found"), 404
            
        app.logger.info(f'Playlist deleted: {name}')
        return jsonify(message="Playlist deleted"), 200
        
    except Exception as e:
        app.logger.error(f'Error deleting playlist: {str(e)}')
        return jsonify(error=f"Failed to delete playlist: {str(e)}"), 500

@app.route('/playlists/<name>', methods=['GET'])
def get_playlist(name):
    app.logger.debug(f'GET request received on get_playlist endpoint for name: {name}')
    
    try:
        playlist = mongo.db.playlists.find_one({'name': name})
        if not playlist:
            return jsonify(error="Playlist not found"), 404
            
        return jsonify(playlist), 200
        
    except Exception as e:
        app.logger.error(f'Error retrieving playlist: {str(e)}')
        return jsonify(error=f"Failed to retrieve playlist: {str(e)}"), 500

@app.route('/playlists', methods=['GET'])
def get_all_playlists():
    app.logger.debug('GET request received on get_all_playlists endpoint')
    
    try:
        # Add pagination
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        skip = (page - 1) * per_page
        
        playlists = list(mongo.db.playlists.find().skip(skip).limit(per_page))
        total = mongo.db.playlists.count_documents({})
        
        return jsonify({
            'playlists': playlists,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page if total > 0 else 0
        }), 200
        
    except Exception as e:
        app.logger.error(f'Error retrieving playlists: {str(e)}')
        return jsonify(error=f"Failed to retrieve playlists: {str(e)}"), 500

@app.route('/playlists', methods=['DELETE'])
def delete_all_playlists():
    app.logger.debug('DELETE request received on delete_all_playlists endpoint')
    
    try:
        result = mongo.db.playlists.delete_many({})
        app.logger.warning(f'All playlists deleted: {result.deleted_count} items')
        return jsonify(
            message="All playlists deleted", 
            deleted_count=result.deleted_count
        ), 200
        
    except Exception as e:
        app.logger.error(f'Error deleting all playlists: {str(e)}')
        return jsonify(error=f"Failed to delete all playlists: {str(e)}"), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        mongo.db.command('ping')
        return jsonify(status="healthy"), 200
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return jsonify(status="unhealthy", error=str(e)), 503

# if __name__ == '__main__':
#     print("Starting Playlists API...")
#     print(f"MongoDB URI: {mongo_uri}")
#     print("Server starting on http://0.0.0.0:5000")
#     app.run(debug=False, host='0.0.0.0', port=5000)