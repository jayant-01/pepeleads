from flask import Flask
from index import index_bp, db as index_db
from page2 import page2_bp
from page3 import page3_bp
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey_response.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)  # Required for session support

# Initialize the Page 1 database with our app
index_db.init_app(app)

# Register Blueprints
app.register_blueprint(index_bp)         # Handles index.html at '/'
app.register_blueprint(page2_bp)         # Handles page2.html at '/page2'
app.register_blueprint(page3_bp)         # Handles page3.html at '/page3'

# Create the tables only if they don't exist
with app.app_context():
    # Create all tables without dropping existing ones
    index_db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
