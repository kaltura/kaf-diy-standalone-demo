#!/usr/bin/env python3
"""
KAF Standalone Demo - Entry Point
Run this script to start the Flask application
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Add the lib directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from flask import Flask, send_from_directory
import os
from .routes import api_bp

# Enable KalturaClient logging before any clients are created
from .kaltura_integration.logging_wrapper import enable_kaltura_logging

def create_app():
    """Create and configure Flask application"""
    # Enable KalturaClient logging for all future client instances
    enable_kaltura_logging()
    
    app = Flask(__name__, static_folder='../public', static_url_path='')
    
    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Serve static files
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/entry-diy')
    def entry_create_kaf():
        return send_from_directory(app.static_folder, 'pages/entry-diy/index.html')
    
    @app.route('/create-sub-tenant')
    def create_sub_tenant():
        return send_from_directory(app.static_folder, 'pages/create-sub-tenant/index.html')
    
    return app

def main():
    """Main application entry point"""
    try:
        # Create Flask app
        app = create_app()
        
        # Get configuration from environment variables
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', '3033'))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        # Run the application
        print(f"🚀 Starting KAF Standalone Demo Server")
        print(f"🌐 HTTP Server running on http://{host}:{port}")
        print(f"📱 Main Application: http://localhost:{port}/")
        print(f"📱 Entry Create DIY: http://localhost:{port}/entry-diy")
        print(f"📱 Create Sub Tenant: http://localhost:{port}/create-sub-tenant")
        print(f"🔧 Debug Mode: {debug}")
        print(f"📝 KalturaClient logging: ENABLED - All API requests/responses will be logged")
        
        app.run(
            host=host,
            port=port,
            debug=debug
        )
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please check your environment variables and ensure all required variables are set.")
    except Exception as e:
        print(f"❌ Server Error: {e}")

if __name__ == '__main__':
    main() 