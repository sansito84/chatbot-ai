import os
import threading
import time
from collections import OrderedDict

from google import genai
from google.genai import types

# Modelo configurable por variable de entorno para poder actualizarlo sin tocar código
DEFAULT_MODEL = "gemini-3.8-flash"
# Límite de conversaciones en memoria y tiempo de inactividad antes de descartarlas
MAX_SESSIONS = 500
SESSION_TTL_SECONDS = 60 * 60


class GeminiChatbot:
    def __init__(self):
        self.context = self.load_context()
        self.system_prompt = (
            "Eres AmikBot, el asistente virtual del portfolio de Santiago Sito, desarrollador Full-stack y DevOps. "
            "Quien te escribe suele ser un posible cliente o reclutador que quiere saber si Santiago le sirve.\n\n"
            "Cómo responder:\n"
            "- Contesta exactamente lo que te preguntan, en la primera oración. Sin saludos, rodeos ni repetir la pregunta.\n"
            "- Sé breve: 1 a 3 oraciones (máximo 50 palabras). Usa una lista solo si piden enumerar algo.\n"
            "- Habla de Santiago en tercera persona y usa datos concretos (empresas, fechas, tecnologías) de la información de abajo.\n"
            "- Si el dato no está en la información, dilo en una frase y ofrece su contacto. Nunca inventes experiencia, precios ni disponibilidad.\n"
            "- Preséntate en una sola oración únicamente si el usuario solo saluda o pregunta quién eres.\n"
            "- No termines cada respuesta con una pregunta. Ofrece el contacto solo si preguntan cómo contratarlo o contactarlo, o si no tienes el dato.\n"
            "- Si preguntan algo ajeno a Santiago y su trabajo, indica en una frase que solo puedes responder sobre él.\n"
            "- Responde en el idioma del usuario, con tono profesional y cercano.\n"
            "- Formato: HTML simple (<p>, <ul>, <li>, <strong>, <a href>), sin títulos ni encabezados.\n\n"
            "Ejemplos:\n"
            "Usuario: ¿Sabe Docker?\n"
            "AmikBot: <p>Sí. Usa <strong>Docker y Kubernetes</strong> para automatizar despliegues en sus proyectos freelance desde 2024.</p>\n"
            "Usuario: ¿Cuánto cobra?\n"
            "AmikBot: <p>No tengo esa información; depende del proyecto. Puedes consultarle directamente a "
            "<a href=\"mailto:santiagosito@gmail.com\">santiagosito@gmail.com</a>.</p>"
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
        # Reintentar ante errores temporales de Google (429, 500, 503...),
        # con esperas cortas para no superar el timeout de gunicorn (30 s)
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=3, initial_delay=1, max_delay=4),
            ),
        )
        self.model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

        # Configuración del modelo
        self.generation_config = types.GenerateContentConfig(
            system_instruction=f"{self.system_prompt}\n\n{self.create_context_text()}",
            temperature=0.4,  # Respuestas más precisas y consistentes
            top_p=0.9,        # Diversidad controlada
            top_k=50,         # Opciones variadas
            max_output_tokens=2048,  # Margen para el razonamiento; el largo lo limita el prompt
            # Razonamiento bajo para responder rápido (modelos Gemini 3)
            thinking_config=types.ThinkingConfig(thinking_level="low"),
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
                "sitio_web": "https://santiagosito.netlify.app/"
            }
        }
        return context

    def create_context_text(self):
        # Resumir el contexto como texto para las instrucciones del sistema
        experiencia = "\n".join(
            f"- {exp['puesto']} en {exp['empresa']} ({exp['periodo']}): " + " ".join(exp['responsabilidades'])
            for exp in self.context['experiencia_laboral']
        )
        estudios = "\n".join(
            f"- {edu['curso']} en {edu['institución']} ({edu['periodo']})" for edu in self.context['estudios']
        )
        contacto = "\n".join(f"- {canal}: {valor}" for canal, valor in self.context['contacto'].items())
        return (
            "Información sobre Santiago Sito:\n\n"
            f"Experiencia laboral:\n{experiencia}\n\n"
            f"Habilidades técnicas: {', '.join(self.context['skills'])}.\n"
            f"Habilidades blandas: {' '.join(self.context['soft_skills'])}\n\n"
            f"Estudios:\n{estudios}\n\n"
            f"Contacto:\n{contacto}"
        )

    def get_response(self, question, session_id):
        # Enviar la pregunta a la conversación de este usuario
        chat = self.get_chat(session_id)
        response = chat.send_message(question)
        return response.text
