import os
import google.generativeai as genai

class GeminiChatbot:
    def __init__(self):
        self.init_gemini_chatbot()
        self.context = self.load_context()

    def init_gemini_chatbot(self):
        # Configuración de la API Key
        genai.configure(api_key=os.getenv("API_KEY"))
        
        # Configuración del modelo
        generation_config = {
            "temperature": 0.7,  # Un poco de creatividad
            "top_p": 0.9,        # Diversidad controlada
            "top_k": 50,         # Opciones variadas
            "max_output_tokens": 300,  # Limitar la longitud de la respuesta
            "response_mime_type": "text/plain",
        }
        # Inicializar el modelo Gemini
        gemini = genai.GenerativeModel(model_name="gemini-1.5-pro-exp-0827",
                                       generation_config=generation_config)
        self.chatbot = gemini.start_chat()

    def load_context(self):
        # Definir el contexto basado en tu experiencia
        context = {
            "experiencia_laboral": [
                "Trabajé en Covery Tech S.A. como CTO y Developer de febrero de 2022 a febrero de 2024.",
                "Participé en proyectos como Techo y Yendo.ar utilizando Node.js."
            ],
            "skills": [
                "Programación en JavaScript, Python.",
                "Uso de herramientas como Express, React, y MySQL.",
                "Experiencia con PM2 y servidores en AWS y GCP."
            ],
            "soft_skills": [
                "Habilidades interpersonales y de comunicación.",
                "Capacidad para trabajar en equipo y liderar proyectos.",
                "Organización y gestión de tiempo."
            ],
            "estudios": [
                "Formación en programación con Python y Flask.",
                "Conocimientos en desarrollo web y administración de servidores."
            ],
            "contacto": {
                "email": "santiago@example.com",  # Reemplaza con tu correo real
                "whatsapp": "https://wa.me/1234567890"  # Reemplaza con tu enlace de WhatsApp real
            }
        }
        return context

    def create_prompt(self, question):
        # Crear un prompt que incluye el contexto y la pregunta
        context_text = "\n".join([
            f"Mi experiencia laboral incluye: {', '.join(self.context['experiencia_laboral'])}.",
            f"Mis habilidades son: {', '.join(self.context['skills'])}.",
            f"Mis habilidades blandas incluyen: {', '.join(self.context['soft_skills'])}.",
            f"He estudiado: {', '.join(self.context['estudios'])}.",
            f"Puedes contactarme por correo electrónico a {self.context['contacto']['email']} o a través de WhatsApp en {self.context['contacto']['whatsapp']}."
        ])
        prompt = f"{context_text}\n\nPregunta: {question}"
        return prompt

    def get_response(self, question):
        # Crear el prompt personalizado
        prompt = self.create_prompt(question)
        
        # Enviar la pregunta al modelo generativo
        response = self.chatbot.send_message(prompt)
        
        return response.text
