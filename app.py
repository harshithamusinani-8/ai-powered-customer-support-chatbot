import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from database.db import (
    init_db, create_user, create_conversation, get_conversation_history,
    save_message, save_interaction, get_logs
)
from nlp.processor import preprocess_text
from models.chatbot_model import ChatbotModel

load_dotenv()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

init_db()
chatbot = ChatbotModel()


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/conversations")
def start_conversation():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "Guest")).strip()[:100] or "Guest"

    try:
        user_id = create_user(name)
        conversation_id = create_conversation(user_id)
        return jsonify({
            "success": True,
            "user_id": user_id,
            "conversation_id": conversation_id
        }), 201
    except Exception:
        app.logger.exception("Could not create conversation")
        return jsonify({"success": False, "error": "Could not start a new conversation."}), 500


@app.get("/api/conversations/<int:conversation_id>/messages")
def conversation_history(conversation_id):
    try:
        history = get_conversation_history(conversation_id)
        return jsonify({"success": True, "messages": history})
    except Exception:
        app.logger.exception("Could not retrieve conversation history")
        return jsonify({"success": False, "error": "Could not retrieve conversation history."}), 500


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    conversation_id = data.get("conversation_id")
    message = str(data.get("message", "")).strip()

    if not conversation_id:
        return jsonify({"success": False, "error": "conversation_id is required."}), 400

    if not message:
        return jsonify({"success": False, "error": "Please enter a message."}), 400

    if len(message) > 1000:
        return jsonify({"success": False, "error": "Message is too long. Please keep it under 1000 characters."}), 400

    try:
        conversation_id = int(conversation_id)
        history = get_conversation_history(conversation_id)

        cleaned = preprocess_text(message)
        result = chatbot.generate_response(
            user_message=message,
            cleaned_message=cleaned,
            history=history
        )

        save_message(conversation_id, "user", message)
        save_message(conversation_id, "bot", result["response"])

        save_interaction(
            conversation_id=conversation_id,
            user_query=message,
            bot_response=result["response"],
            intent=result["intent"],
            confidence=result["confidence"],
            source=result["source"]
        )

        return jsonify({
            "success": True,
            "response": result["response"],
            "intent": result["intent"],
            "confidence": result["confidence"],
            "source": result["source"]
        })

    except ValueError:
        return jsonify({"success": False, "error": "Invalid conversation ID."}), 400
    except Exception:
        app.logger.exception("Chat processing error")
        return jsonify({
            "success": False,
            "error": "Sorry, something went wrong while processing your message."
        }), 500


@app.get("/api/logs")
def logs():
    # Basic demonstration endpoint for viewing interaction logs.
    # For a production deployment, protect this endpoint with authentication.
    try:
        limit = min(max(int(request.args.get("limit", 100)), 1), 500)
        return jsonify({"success": True, "logs": get_logs(limit)})
    except Exception:
        app.logger.exception("Could not retrieve logs")
        return jsonify({"success": False, "error": "Could not retrieve logs."}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
