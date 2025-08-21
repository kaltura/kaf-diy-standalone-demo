from flask import Blueprint, request, jsonify, Response
from .services.kaltura_service import KalturaService
import json
import queue
import threading
import time
import os

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Global queue for progress updates
progress_queue = queue.Queue()

def send_progress_update(message, step=None, data=None):
    """Send a progress update to all connected clients"""
    update = {
        'timestamp': time.time(),
        'message': message,
        'step': step,
        'data': data
    }
    progress_queue.put(update)

@api_bp.route('/kaltura/progress-stream')
def progress_stream():
    """Server-Sent Events endpoint for streaming progress updates"""
    def generate():
        while True:
            try:
                # Wait for updates with timeout
                update = progress_queue.get(timeout=30)
                yield f"data: {json.dumps(update)}\n\n"
            except queue.Empty:
                # Send keepalive
                yield f"data: {json.dumps({'timestamp': time.time(), 'type': 'keepalive'})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


@api_bp.route('/kaltura/generate-session', methods=['POST'])
def generate_session():
    """Generate a Kaltura session token for embedded rooms"""
    data = request.get_json()
    return KalturaService.generate_session(data)

@api_bp.route('/kaltura/add-room', methods=['POST'])
def add_room():
    """Add a new room entry"""
    data = request.get_json()
    return KalturaService.add_room_session(data)

@api_bp.route('/kaltura/create-room-with-live', methods=['POST'])
def create_room_with_live():
    """Create a room with automatic live entry creation"""
    data = request.get_json()
    return KalturaService.create_diy(data)

@api_bp.route('/kaltura/session-detail', methods=['POST'])
def get_session_detail():
    """Get session details by entry ID"""
    data = request.get_json()
    return KalturaService.get_session_details(data)

@api_bp.route('/kaltura/add-live', methods=['POST'])
def add_live():
    """Add a new live session"""
    data = request.get_json()
    return KalturaService.add_live_session(data)

@api_bp.route('/kaltura/create-sub-tenant', methods=['POST'])
def create_sub_tenant():
    """Create a new Kaltura sub-tenant"""
    data = request.get_json()
    return KalturaService.create_sub_tenant(data)



@api_bp.route('/kaltura/create-publishing-category', methods=['POST'])
def create_publishing_category():
    """Create a publishing category under MediaSpace>site>channels"""
    data = request.get_json()
    return KalturaService.create_publishing_category(data)

@api_bp.route('/kaltura/env-info', methods=['GET'])
def get_env_info():
    """Get environment variables including parent PID and template PID"""
    env_info = {
        'kaltura_parent_partner_id': os.getenv('KALTURA_PARENT_PARTNER_ID', 'Not set'),
        'kaltura_template_partner_id': os.getenv('KALTURA_TEMPLATE_PARTNER_ID', 'Not set'),
    }
    return jsonify(env_info) 