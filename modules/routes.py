from flask import Blueprint

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/')
def home():
    return "¡Bienvenido al chatbot IA!"

@api_blueprint.route('/hello', methods=['GET'])
def hello():
    return "Hola desde Flask!"
