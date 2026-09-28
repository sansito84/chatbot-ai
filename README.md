# chatbot-ai

AmikBot: API en Flask que responde preguntas sobre Santiago Sito usando Gemini.

## Configuración

Variables de entorno:

- `GEMINI_API_KEY` (o `API_KEY`): API key de Google AI Studio. **Obligatoria.**
- `GEMINI_MODEL` (opcional): modelo a usar. Por defecto `gemini-2.5-flash`.

## Uso

```bash
pip install -r requirements.txt
GEMINI_API_KEY=tu_key python app.py
```

`POST /chat` con `{"question": "...", "session_id": "..."}`. El `session_id` es opcional:
si no se envía, la respuesta incluye uno nuevo, que el frontend debe reenviar en los
siguientes mensajes para mantener la conversación de ese usuario.

Las conversaciones se guardan en memoria, así que en producción se debe correr con un
solo worker de gunicorn (el valor por defecto del `Procfile`).
