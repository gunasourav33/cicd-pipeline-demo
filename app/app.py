import logging
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure logging with request ID
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory storage
items_db = {}


class RequestIDFilter(logging.Filter):
    """Add request ID to log context."""
    def filter(self, record):
        record.request_id = getattr(request, 'request_id', 'no-req-id')
        return True


logger.addFilter(RequestIDFilter())


@app.before_request
def before_request():
    """Generate request ID for tracing."""
    request.request_id = str(uuid.uuid4())[:8]
    logger.info(f"Incoming {request.method} {request.path}")


@app.after_request
def after_request(response):
    """Log response status."""
    logger.info(f"Response {response.status_code}")
    return response


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/items', methods=['GET'])
def list_items():
    try:
        items = [
            {'id': item_id, **item_data}
            for item_id, item_data in items_db.items()
        ]
        logger.info(f"Listed {len(items)} items")
        return jsonify({'items': items}), 200
    except Exception as e:
        logger.error(f"Error listing items: {str(e)}")
        return jsonify({'error': 'Failed to list items'}), 500


@app.route('/items', methods=['POST'])
def create_item():
    try:
        data = request.get_json()

        if not data or 'name' not in data:
            return jsonify({'error': 'name field is required'}), 400

        if 'description' not in data:
            return jsonify({'error': 'description field is required'}), 400

        item_id = str(uuid.uuid4())
        items_db[item_id] = {
            'name': data['name'],
            'description': data['description'],
            'created_at': datetime.utcnow().isoformat()
        }

        logger.info(f"Created item {item_id}: {data['name']}")
        return jsonify({'id': item_id, **items_db[item_id]}), 201

    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        return jsonify({'error': 'Failed to create item'}), 500


@app.route('/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        if item_id not in items_db:
            return jsonify({'error': 'Item not found'}), 404

        item_name = items_db[item_id]['name']
        del items_db[item_id]
        logger.info(f"Deleted item {item_id}: {item_name}")
        return jsonify({'message': 'Item deleted'}), 200
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete item'}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
