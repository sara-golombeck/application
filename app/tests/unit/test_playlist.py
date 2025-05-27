import pytest
from unittest.mock import patch
import json
from app.app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    return app.test_client()

@patch('app.mongo')
def test_add_playlist_success(mock_mongo, client):
    """Test - Successfully create a new playlist"""
    mock_mongo.db.playlists.find_one.return_value = None
    mock_mongo.db.playlists.insert_one.return_value.inserted_id = "123456"
    
    playlist_data = {
        "songs": ["song1", "song2"],
        "genre": "rock"
    }
    
    response = client.post(
        '/playlists/test_playlist',
        data=json.dumps(playlist_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'test_playlist'
    assert 'message' in data

@patch('app.mongo')
def test_add_playlist_already_exists(mock_mongo, client):
    """Test - Playlist already exists"""
    mock_mongo.db.playlists.find_one.return_value = {"name": "test_playlist"}
    
    playlist_data = {"songs": ["song1"]}
    
    response = client.post(
        '/playlists/test_playlist',
        data=json.dumps(playlist_data),
        content_type='application/json'
    )
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.mongo')
def test_get_playlist_success(mock_mongo, client):
    """Test - Retrieve existing playlist"""
    mock_playlist = {
        "name": "test_playlist",
        "songs": ["song1", "song2"]
    }
    mock_mongo.db.playlists.find_one.return_value = mock_playlist
    
    response = client.get('/playlists/test_playlist')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'test_playlist'

@patch('app.mongo')
def test_get_playlist_not_found(mock_mongo, client):
    """Test - Playlist not found"""
    mock_mongo.db.playlists.find_one.return_value = None
    
    response = client.get('/playlists/nonexistent')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.mongo')
def test_delete_playlist_success(mock_mongo, client):
    """Test - Successfully delete playlist"""
    mock_mongo.db.playlists.delete_one.return_value.deleted_count = 1
    
    response = client.delete('/playlists/test_playlist')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data

def test_invalid_json(client):
    """Test - Invalid JSON request"""
    response = client.post(
        '/playlists/test_playlist',
        data="invalid json",
        content_type='application/json'
    )
    
    assert response.status_code == 400

@patch('app.mongo')
def test_health_check_healthy(mock_mongo, client):
    """Test - Health check returns healthy status"""
    mock_mongo.db.command.return_value = True
    
    response = client.get('/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

# Bonus: Parametrized test (not possible in unittest without repetition)
@pytest.mark.parametrize("playlist_name,expected_status", [
    ("valid-playlist", 201),
    ("another-valid-name", 201),
    ("playlist-with-numbers-123", 201),
])
@patch('app.mongo')
def test_playlist_creation_with_various_names(mock_mongo, client, playlist_name, expected_status):
    """Test - Playlist creation with various valid names"""
    mock_mongo.db.playlists.find_one.return_value = None
    mock_mongo.db.playlists.insert_one.return_value.inserted_id = "123456"
    
    playlist_data = {"songs": ["song1"], "genre": "rock"}
    
    response = client.post(
        f'/playlists/{playlist_name}',
        data=json.dumps(playlist_data),
        content_type='application/json'
    )
    
    assert response.status_code == expected_status
    if expected_status == 201:
        data = json.loads(response.data)
        assert data['name'] == playlist_name

# Additional test for error scenarios
@pytest.mark.parametrize("mock_error,expected_status", [
    (Exception("Database connection failed"), 500),
    (Exception("Timeout error"), 500),
])
@patch('app.mongo')
def test_database_error_handling(mock_mongo, client, mock_error, expected_status):
    """Test - Database error handling"""
    mock_mongo.db.playlists.find_one.side_effect = mock_error
    
    response = client.get('/playlists/test_playlist')
    
    assert response.status_code == expected_status



















# import unittest
# from unittest.mock import patch, MagicMock
# import json
# from flask import Flask
# from app import app 


# class PlaylistAPITestCase(unittest.TestCase):
#     def setUp(self):
#         """Setup tests"""
#         self.app = app
#         self.app.config['TESTING'] = True
#         self.client = self.app.test_client()
        
#     @patch('app.mongo')
#     def test_add_playlist_success(self, mock_mongo):
#         """Test - Successfully create a new playlist"""
#         mock_mongo.db.playlists.find_one.return_value = None 
#         mock_mongo.db.playlists.insert_one.return_value.inserted_id = "123456"
        
#         playlist_data = {
#             "songs": ["song1", "song2"],
#             "genre": "rock"
#         }
        
#         response = self.client.post(
#             '/playlists/test_playlist',
#             data=json.dumps(playlist_data),
#             content_type='application/json'
#         )
        
#         self.assertEqual(response.status_code, 201)
#         data = json.loads(response.data)
#         self.assertEqual(data['name'], 'test_playlist')
#         self.assertIn('message', data)

#     @patch('app.mongo')
#     def test_add_playlist_already_exists(self, mock_mongo):
#         """Test - Playlist already exists"""
#         mock_mongo.db.playlists.find_one.return_value = {"name": "test_playlist"}
        
#         playlist_data = {"songs": ["song1"]}
        
#         response = self.client.post(
#             '/playlists/test_playlist',
#             data=json.dumps(playlist_data),
#             content_type='application/json'
#         )
        
#         self.assertEqual(response.status_code, 409)
#         data = json.loads(response.data)
#         self.assertIn('error', data)

#     @patch('app.mongo')
#     def test_get_playlist_success(self, mock_mongo):
#         """Test - Retrieve existing playlist"""
#         mock_playlist = {
#             "name": "test_playlist",
#             "songs": ["song1", "song2"]
#         }
#         mock_mongo.db.playlists.find_one.return_value = mock_playlist
        
#         response = self.client.get('/playlists/test_playlist')
        
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertEqual(data['name'], 'test_playlist')

#     @patch('app.mongo')
#     def test_get_playlist_not_found(self, mock_mongo):
#         """Test - Playlist not found"""
#         mock_mongo.db.playlists.find_one.return_value = None
        
#         response = self.client.get('/playlists/nonexistent')
        
#         self.assertEqual(response.status_code, 404)
#         data = json.loads(response.data)
#         self.assertIn('error', data)

#     @patch('app.mongo')
#     def test_delete_playlist_success(self, mock_mongo):
#         """Test - Successfully delete playlist"""
#         mock_mongo.db.playlists.delete_one.return_value.deleted_count = 1
        
#         response = self.client.delete('/playlists/test_playlist')
        
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertIn('message', data)

#     def test_invalid_json(self):
#         """Test - Invalid JSON"""
#         response = self.client.post(
#             '/playlists/test_playlist',
#             data="invalid json",
#             content_type='application/json'
#         )
        
#         self.assertEqual(response.status_code, 400)

#     @patch('app.mongo')
#     def test_health_check_healthy(self, mock_mongo):
#         """Test - Health check is healthy"""
#         mock_mongo.db.command.return_value = True
        
#         response = self.client.get('/health')
        
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertEqual(data['status'], 'healthy')


# if __name__ == '__main__':
#     unittest.main()
