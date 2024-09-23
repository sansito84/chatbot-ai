from app.chatbot import GeminiChatbot
from flask import Flask, request, jsonify
from flask_cors import CORS

# Inicializar Flask y el chatbot
app = Flask(__name__)
chatbot = GeminiChatbot()

CORS(app, resources={r"/chat": {"origins": "*"}})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()

    # Verificar si la solicitud contiene la pregunta
    if 'question' not in data:
        return jsonify({'error': 'Falta el campo "question"'}), 400
    
    # Obtener la pregunta
    question = data['question']
    
    # Obtener la respuesta del chatbot
    try:
        response = chatbot.get_response(question)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Cambia el puerto a 5000 o 8000

