from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.gemini_handler import GeminiHandler
from utils.twilio_handler import TwilioHandler
from database.chromadb_manager import ChromaDBManager
from services.health_tips import HealthTipsService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize handlers
gemini_handler = GeminiHandler(api_key=os.getenv('GOOGLE_API_KEY'))
twilio_handler = TwilioHandler()
db_manager = ChromaDBManager(os.path.join(os.path.dirname(__file__), '..', 'data', 'chromadb'))

# Initialize RAG
gemini_handler.set_rag_handler(db_manager)

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Health chatbot API is running"
    })

@app.route('/chat', methods=['POST'])
async def chat():
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        message = data.get('message')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Get response from Gemini
        response = await gemini_handler.get_response(user_id, message)
        
        # Store chat history
        db_manager.store_chat(user_id, message, response)
        
        return jsonify({
            "response": response,
            "user_id": user_id
        })

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Failed to process chat message"}), 500

@app.route('/whatsapp/webhook', methods=['POST'])
async def whatsapp_webhook():
    try:
        # Get incoming WhatsApp message details
        incoming_msg = request.values.get('Body', '').strip()
        sender = request.values.get('From', '').strip()
        
        print(f"Received WhatsApp message: {incoming_msg} from {sender}")
        
        if not incoming_msg:
            return twilio_handler.create_response("Message is required")

        # Get response from Gemini
        response = await gemini_handler.get_response(sender, incoming_msg)
        
        # Store chat history
        db_manager.store_chat(sender, incoming_msg, response)
        
        # Create and return WhatsApp response
        return twilio_handler.create_response(response)

    except Exception as e:
        print(f"Error in WhatsApp webhook: {str(e)}")
        return twilio_handler.create_response("Sorry, I couldn't process your message")

@app.route('/whatsapp/status', methods=['POST'])
def whatsapp_status():
    try:
        # Get message status details
        message_sid = request.values.get('MessageSid', '')
        message_status = request.values.get('MessageStatus', '')
        
        print(f"Message {message_sid} status: {message_status}")
        
        return jsonify({
            "status": "success",
            "message": f"Status update received: {message_status}"
        })
        
    except Exception as e:
        print(f"Error in status webhook: {str(e)}")
        return jsonify({"error": "Failed to process status update"}), 500

@app.route('/tips/random', methods=['GET'])
def get_random_tip():
    try:
        tips_service = HealthTipsService(db_manager)
        tip = tips_service.get_random_tip()
        return jsonify({
            "tip": tip.get('tip', "Remember to maintain a healthy lifestyle!"),
            "category": tip.get('category', "general_health")
        })
    except Exception as e:
        print(f"Error in random tip endpoint: {str(e)}")
        return jsonify({
            "tip": "Remember to maintain a healthy lifestyle!",
            "category": "general_health"
        })

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if rating is None:
            return jsonify({"error": "Rating is required"}), 400

        # Store feedback in database
        db_manager.store_feedback(user_id, rating, comment)
        
        return jsonify({
            "message": "Thank you for your feedback!",
            "status": "success"
        })
    except Exception as e:
        print(f"Error in feedback endpoint: {str(e)}")
        return jsonify({"error": "Failed to process feedback"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)