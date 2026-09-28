import uuid

from flask import Flask, request, jsonify
from flask_cors import CORS
from modules.chatbot import GeminiChatbot

# Inicializar Flask y el chatbot
app = Flask(__name__)
chatbot = GeminiChatbot()

CORS(app, resources={r"/chat": {"origins": "*"}})

@app.route('/')
def home():
    return "¡Bienvenido al chatbot IA!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)

    # Verificar si la solicitud contiene la pregunta
    if not isinstance(data, dict) or not str(data.get('question', '')).strip():
        return jsonify({'error': 'Falta el campo "question"'}), 400

    # Obtener la pregunta
    question = str(data['question']).strip()

    # Cada usuario tiene su propia conversación; si no envía session_id se crea uno nuevo
    session_id = str(data.get('session_id') or uuid.uuid4())

    # Obtener la respuesta del chatbot
    try:
        response = chatbot.get_response(question, session_id)
        return jsonify({'response': response, 'session_id': session_id})
    except Exception:
        app.logger.exception("Error al obtener la respuesta del chatbot")
        return jsonify({'error': 'No se pudo obtener una respuesta, intenta de nuevo más tarde.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Cambia el puerto a 5000 o 8000
