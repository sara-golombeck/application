db = db.getSiblingDB('playlists_db');

db.createUser({
  user: 'playlists_user',
  pwd: 'playlist123',
  roles: [
    {
      role: 'readWrite',
      db: 'playlists_db'
    }
  ]
});

db.playlists.createIndex({ "name": 1 }, { unique: true });
db.playlists.createIndex({ "created_at": 1 });
db.playlists.createIndex({ "genre": 1 });

print("Database and user created successfully!");