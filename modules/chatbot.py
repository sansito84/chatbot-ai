import os
import google.generativeai as genai


class GeminiChatbot:
    def __init__(self):
        self.init_gemini_chatbot()
        self.context = self.load_context()
        self.system_prompt = (
            "Eres un asistente virtual avanzado creado con un LLM, "
            "y tu nombre es AmikBot el Asistente Virtual desarrollado por Santiago Sito. "
            "Debes hablar en nombre de Santiago Sito, ofrecer ayuda amigable "
            "y mantener un tono profesional en todas tus respuestas siempre recordando que se le está hablando a un posible contratante o cliente."
            "Debes dar respuestas concisas, y cortas (no más de 50 palabras por respuesta) y brindar siempre invitacion al diálogo"
            "Tu presentación debes hacerla una sola vez por cada usuario"
        )

    def init_gemini_chatbot(self):
        # Configuración de la API Key
        genai.configure(api_key=os.getenv("API_KEY"))
        
        # Configuración del modelo
        generation_config = {
            "temperature": 0.8,  # Un poco de creatividad
            "top_p": 0.9,        # Diversidad controlada
            "top_k": 50,         # Opciones variadas
            "max_output_tokens": 500,  # Limitar la longitud de la respuesta
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
                {
                    "puesto": "Full-stack Developer y DevOps",
                    "empresa": "Freelance",
                    "periodo": "Feb 2024 - Actualidad",
                    "responsabilidades": [
                        "Desarrollo de soluciones full-stack con Node.js, React.js, Python y MySQL.",
                        "Automatización de procesos con Docker, Kubernetes y Nginx.",
                        "Uso de modelos de lenguaje (LLMs) para mejorar funcionalidades en aplicaciones de procesamiento de lenguaje natural."
                    ]
                },
                {
                    "puesto": "Full-stack Developer y DevOps",
                    "empresa": "Covery Tech S.A.",
                    "periodo": "Feb 2022 - Feb 2024",
                    "responsabilidades": [
                        "Desarrollo de software para la gestión de ventas de seguros online.",
                        "Implementación de soluciones full-stack con Node.js, React.js y MySQL.",
                        "Automatización de procesos con PM2 y Nginx."
                    ]
                },
                {
                    "puesto": "Full-stack Developer y DevOps",
                    "empresa": "Yendo.ar",
                    "periodo": "Dic 2022 - Sept 2023",
                    "responsabilidades": [
                        "Desarrollo de aplicación web tipo CRUD para negocios y emprendimientos.",
                        "Implementación de pasarelas de pago y autogestión de perfiles de usuarios."
                    ]
                },
                {
                    "puesto": "Fundador y CEO",
                    "empresa": "Aladelta Muebles de Autor",
                    "periodo": "Ene 2012 - Ene 2022",
                    "responsabilidades": [
                        "Diseño y armado de muebles personalizados.",
                        "Implementación de soluciones CAD-CAM."
                    ]
                }
            ],
            "skills": [
                "JavaScript", "Node.js", "Express.js", "React.js", "Next.js", "Python", 
                "Docker", "Kubernetes", "MySQL", "MongoDB", "Linux", "Git", "CI/CD"
            ],
            "soft_skills": [
                "Habilidades interpersonales y de comunicación.",
                "Capacidad para trabajar en equipo y liderar proyectos.",
                "Organización y gestión de tiempo.",
                "Aprendizaje continuo"
            ],
            "estudios": [
                {
                    "institución": "OpenBootcamp",
                    "curso": "TypeScript",
                    "periodo": "Sept 2024 - Oct 2024"
                },
                {
                    "institución": "Codo a Codo 4.0",
                    "curso": "Desarrollador Fullstack Python",
                    "periodo": "Feb 2024 - Jul 2024"
                },
                {
                    "institución": "Codo a Codo 4.0",
                    "curso": "Desarrollador FullStack JS",
                    "periodo": "Feb 2023 - Jul 2023"
                }
            ],
            "contacto": {
                "email": "santiagosito@gmail.com",
                "whatsapp": "https://wa.me/3442453430",
                "GitHub": "https://github.com/sansito84",
                "LinkedIn": "https://www.linkedin.com/in/santiagosito",
                "sitio_web": "https://endearing-faloodeh-1fe71b.netlify.app/"  # Reemplaza con tu enlace de WhatsApp real
            }
        }
        return context

    def create_prompt(self, question):
        # Crear un prompt que incluye el contexto, el rol del asistente, y la pregunta
        context_text = "\n".join([
            f"Mi experiencia laboral incluye: {', '.join(self.context['experiencia_laboral'])}.",
            f"Mis habilidades son: {', '.join(self.context['skills'])}.",
            f"Mis habilidades blandas incluyen: {', '.join(self.context['soft_skills'])}.",
            f"He estudiado: {', '.join(self.context['estudios'])}.",
            f"Puedes contactarme por correo electrónico a {self.context['contacto']['email']} o a través de WhatsApp en {self.context['contacto']['whatsapp']}."
        ])
        
        prompt = (
            f"{self.system_prompt}\n\n"
            f"{context_text}\n\n"
            f"Pregunta del usuario: {question}\n"
            f"Responde como el Asistente Virtual de Santiago Sito con formatos HTML siendo h3 los headers más grandes."
        )
        return prompt

    def get_response(self, question):
        # Crear el prompt personalizado
        prompt = self.create_prompt(question)
        
        # Enviar la pregunta al modelo generativo
        response = self.chatbot.send_message(prompt)
        
        return response.text
