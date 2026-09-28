import os
import threading
import time
from collections import OrderedDict

from google import genai
from google.genai import types

# Modelo configurable por variable de entorno para poder actualizarlo sin tocar código
DEFAULT_MODEL = "gemini-2.5-flash"
# Límite de conversaciones en memoria y tiempo de inactividad antes de descartarlas
MAX_SESSIONS = 500
SESSION_TTL_SECONDS = 60 * 60


class GeminiChatbot:
    def __init__(self):
        self.context = self.load_context()
        self.system_prompt = (
            "Eres un asistente virtual avanzado creado con un LLM, "
            "y tu nombre es AmikBot el Asistente Virtual desarrollado por Santiago Sito. "
            "Debes hablar en nombre de Santiago Sito, ofrecer ayuda amigable "
            "y mantener un tono profesional en todas tus respuestas siempre recordando que se le está hablando a un posible contratante o cliente. "
            "Debes dar respuestas concisas, y cortas (no más de 50 palabras por respuesta) y brindar siempre invitacion al diálogo. "
            "Tu presentación debes hacerla una sola vez por cada usuario. "
            "Responde con formato HTML, siendo h3 los headers más grandes."
        )
        # Una conversación por usuario: session_id -> (chat, último uso)
        self.sessions = OrderedDict()
        self.lock = threading.Lock()
        self.init_gemini_chatbot()

    def init_gemini_chatbot(self):
        # Configuración de la API Key
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
        if not api_key:
            raise RuntimeError("Falta la variable de entorno GEMINI_API_KEY (o API_KEY)")
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

        # Configuración del modelo
        self.generation_config = types.GenerateContentConfig(
            system_instruction=f"{self.system_prompt}\n\n{self.create_context_text()}",
            temperature=0.8,  # Un poco de creatividad
            top_p=0.9,        # Diversidad controlada
            top_k=50,         # Opciones variadas
            max_output_tokens=500,  # Limitar la longitud de la respuesta
            # Sin "thinking" para que no consuma los tokens de la respuesta
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

    def get_chat(self, session_id):
        # Obtener (o crear) la conversación de este usuario
        now = time.time()
        with self.lock:
            # Descartar conversaciones inactivas
            while self.sessions:
                oldest_id, (_, last_used) = next(iter(self.sessions.items()))
                if now - last_used < SESSION_TTL_SECONDS and len(self.sessions) < MAX_SESSIONS:
                    break
                del self.sessions[oldest_id]

            if session_id in self.sessions:
                chat, _ = self.sessions.pop(session_id)
            else:
                chat = self.client.chats.create(model=self.model, config=self.generation_config)
            self.sessions[session_id] = (chat, now)
            return chat

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

    def create_context_text(self):
        # Resumir el contexto como texto para las instrucciones del sistema
        return "\n".join([
            "Mi experiencia laboral incluye: " + ", ".join(
                [f"{exp['puesto']} en {exp['empresa']} ({exp['periodo']})" for exp in self.context['experiencia_laboral']]
            ) + ".",
            "Mis habilidades son: " + ", ".join(self.context['skills']) + ".",
            "Mis habilidades blandas incluyen: " + ", ".join(self.context['soft_skills']) + ".",
            "He estudiado: " + ", ".join(
                [f"{edu['curso']} en {edu['institución']} ({edu['periodo']})" for edu in self.context['estudios']]
            ) + ".",
            f"Puedes contactarme por correo electrónico a {self.context['contacto']['email']} o a través de WhatsApp en {self.context['contacto']['whatsapp']}."
        ])

    def get_response(self, question, session_id):
        # Enviar la pregunta a la conversación de este usuario
        chat = self.get_chat(session_id)
        response = chat.send_message(question)
        return response.text
