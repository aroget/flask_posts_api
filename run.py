import os
from app import app

port = int(os.environ.get('PORT', 33507))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)