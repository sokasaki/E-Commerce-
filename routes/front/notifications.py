from app import app, db
from flask import Response, session, jsonify, request
import json
import time
import queue
import threading

# Store notification queues per user
user_notifications = {}
notification_lock = threading.Lock()

def get_user_queue(user_id):
    """Get or create a notification queue for a user."""
    with notification_lock:
        if user_id not in user_notifications:
            user_notifications[user_id] = []
        return user_notifications[user_id]

def send_notification(user_id, title, message, ntype='info', duration=5000):
    """Push a notification to a specific user's queue."""
    notification = {
        'title': title,
        'message': message,
        'type': ntype,
        'duration': duration,
        'timestamp': time.time()
    }
    with notification_lock:
        if user_id not in user_notifications:
            user_notifications[user_id] = []
        user_notifications[user_id].append(notification)

def send_notification_to_all_admins(title, message, ntype='order', duration=6000):
    """Send a notification to all admin users."""
    from model.User import User
    with app.app_context():
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            send_notification(admin.id, title, message, ntype, duration)

@app.route('/notifications/stream')
def notification_stream():
    """SSE endpoint for real-time notifications."""
    user_id = session.get('user_id')
    if not user_id:
        return Response('Unauthorized', status=401)

    def event_stream():
        while True:
            # Check for notifications
            with notification_lock:
                notifications = user_notifications.get(user_id, [])
                if notifications:
                    # Pop all pending notifications
                    pending = list(notifications)
                    notifications.clear()
            
            if 'pending' in dir() and pending:
                for notif in pending:
                    yield f"data: {json.dumps(notif)}\n\n"
                pending = []
            
            # Send heartbeat every 15 seconds to keep connection alive
            yield f": heartbeat\n\n"
            time.sleep(2)  # Check every 2 seconds

    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

@app.route('/notifications/test')
def test_notification():
    """Test endpoint to trigger a notification."""
    user_id = session.get('user_id')
    if user_id:
        send_notification(user_id, '🎉 Welcome!', 'Real-time notifications are working!', 'success')
        return jsonify({'status': 'sent'})
    return jsonify({'error': 'Not logged in'}), 401
