import logging
from pythonjsonlogger import jsonlogger
from flask import Flask, request, jsonify, g, render_template
from flask_pymongo import PyMongo
from prometheus_flask_exporter import PrometheusMetrics
import os
import uuid

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

# Configure logging to output JSON format with extra fields
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['service'] = 'playlist-api'
        if hasattr(g, 'request_id'):
            log_record['request_id'] = g.request_id

logHandler = logging.StreamHandler()
formatter = CustomJsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
app.logger.addHandler(logHandler)
app.logger.setLevel(logging.INFO)

# Define loggers for each endpoint
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    g.request_id = str(uuid.uuid4())

@app.route('/', methods=['GET'])
def get_landing():
    app.logger.debug('GET request received on landing endpoint')
    return render_template('index.html')

    # app.logger.debug('Landing page accessed')
    # return jsonify({"service": "Playlists API", "version": "1.0"})

@app.route('/playlists/<name>', methods=['POST'])
def add_playlist(name):
    app.logger.info('Creating playlist', extra={'playlist_name': name, 'method': 'POST'})
    
    if not request.is_json:
        app.logger.warning('Invalid request - not JSON', extra={'content_type': request.content_type})
        return jsonify(error="Request must contain valid JSON"), 400
    
    try:
        playlist = request.json
        if not playlist:
            app.logger.warning('Empty JSON data provided')
            return jsonify(error="Empty JSON data"), 400
            
        playlist['name'] = name
        
        # Check if playlist already exists
        existing = mongo.db.playlists.find_one({'name': name})
        if existing:
            app.logger.warning('Playlist already exists', extra={'playlist_name': name})
            return jsonify(error="Playlist already exists"), 409
            
        result = mongo.db.playlists.insert_one(playlist)
        app.logger.info('Playlist created successfully', extra={
            'playlist_name': name,
            'playlist_id': str(result.inserted_id),
            'songs_count': len(playlist.get('songs', []))
        })
        return jsonify(
            message="Playlist added successfully", 
            name=name,
            id=str(result.inserted_id)
        ), 201
        
    except Exception as e:
        app.logger.error('Failed to create playlist', extra={
            'playlist_name': name,
            'error': str(e)
        })
        return jsonify(error=f"Failed to create playlist: {str(e)}"), 500

@app.route('/playlists/<name>', methods=['PUT'])
def update_playlist(name):
    app.logger.info('Updating playlist', extra={'playlist_name': name, 'method': 'PUT'})
    
    if not request.is_json:
        app.logger.warning('Invalid request - not JSON', extra={'content_type': request.content_type})
        return jsonify(error="Request must contain valid JSON"), 400
    
    try:
        playlist = request.json
        if not playlist:
            app.logger.warning('Empty JSON data provided')
            return jsonify(error="Empty JSON data"), 400
            
        # Don't allow changing the name
        playlist.pop('name', None)
        
        result = mongo.db.playlists.update_one({'name': name}, {'$set': playlist})
        if result.matched_count == 0:
            app.logger.warning('Playlist not found for update', extra={'playlist_name': name})
            return jsonify(error="Playlist not found"), 404
            
        app.logger.info('Playlist updated successfully', extra={
            'playlist_name': name,
            'modified_count': result.modified_count
        })
        return jsonify(message="Playlist updated"), 200
        
    except Exception as e:
        app.logger.error('Failed to update playlist', extra={
            'playlist_name': name,
            'error': str(e)
        })
        return jsonify(error=f"Failed to update playlist: {str(e)}"), 500

@app.route('/playlists/<name>', methods=['DELETE'])
def delete_playlist(name):
    app.logger.info('Deleting playlist', extra={'playlist_name': name, 'method': 'DELETE'})
    
    try:
        result = mongo.db.playlists.delete_one({'name': name})
        if result.deleted_count == 0:
            app.logger.warning('Playlist not found for deletion', extra={'playlist_name': name})
            return jsonify(error="Playlist not found"), 404
            
        app.logger.info('Playlist deleted successfully', extra={'playlist_name': name})
        return jsonify(message="Playlist deleted"), 200
        
    except Exception as e:
        app.logger.error('Failed to delete playlist', extra={
            'playlist_name': name,
            'error': str(e)
        })
        return jsonify(error=f"Failed to delete playlist: {str(e)}"), 500

@app.route('/playlists/<name>', methods=['GET'])
def get_playlist(name):
    app.logger.info('Retrieving playlist', extra={'playlist_name': name, 'method': 'GET'})
    
    try:
        playlist = mongo.db.playlists.find_one({'name': name})
        if not playlist:
            app.logger.warning('Playlist not found', extra={'playlist_name': name})
            return jsonify(error="Playlist not found"), 404
            
        app.logger.info('Playlist retrieved successfully', extra={
            'playlist_name': name,
            'songs_count': len(playlist.get('songs', []))
        })
        return jsonify(playlist), 200
        
    except Exception as e:
        app.logger.error('Failed to retrieve playlist', extra={
            'playlist_name': name,
            'error': str(e)
        })
        return jsonify(error=f"Failed to retrieve playlist: {str(e)}"), 500

@app.route('/playlists', methods=['GET'])
def get_all_playlists():
    app.logger.info('Retrieving all playlists', extra={'method': 'GET'})
    
    try:
        # Add pagination
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        skip = (page - 1) * per_page
        
        playlists = list(mongo.db.playlists.find().skip(skip).limit(per_page))
        total = mongo.db.playlists.count_documents({})
        
        app.logger.info('Playlists retrieved successfully', extra={
            'total_playlists': total,
            'page': page,
            'per_page': per_page,
            'returned_count': len(playlists)
        })
        
        return jsonify({
            'playlists': playlists,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page if total > 0 else 0
        }), 200
        
    except Exception as e:
        app.logger.error('Failed to retrieve playlists', extra={'error': str(e)})
        return jsonify(error=f"Failed to retrieve playlists: {str(e)}"), 500

@app.route('/playlists', methods=['DELETE'])
def delete_all_playlists():
    app.logger.warning('Deleting all playlists - DESTRUCTIVE OPERATION', extra={'method': 'DELETE'})
    
    try:
        result = mongo.db.playlists.delete_many({})
        app.logger.warning('All playlists deleted', extra={'deleted_count': result.deleted_count})
        return jsonify(
            message="All playlists deleted", 
            deleted_count=result.deleted_count
        ), 200
        
    except Exception as e:
        app.logger.error('Failed to delete all playlists', extra={'error': str(e)})
        return jsonify(error=f"Failed to delete all playlists: {str(e)}"), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        mongo.db.command('ping')
        app.logger.info('Health check passed')
        return jsonify(status="healthy"), 200
    except Exception as e:
        app.logger.error('Health check failed', extra={'error': str(e)})
        return jsonify(status="unhealthy", error=str(e)), 503

# if __name__ == '__main__':
#     print("Starting Playlists API...")
#     print(f"MongoDB URI: {mongo_uri}")
#     print("Server starting on http://0.0.0.0:5000")
#     app.run(debug=False, host='0.0.0.0', port=5000)