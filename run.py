import os
from app import app, db

port = int(os.environ.get('PORT', 5000))

if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=port)

