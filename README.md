```markdown
# NEXO AI

NEXO AI es un bot de Telegram con capacidades de inteligencia artificial para responder preguntas y mantener conversaciones.

## Características

- 🤖 Integración con Telegram
- 🧠 Procesamiento de lenguaje natural con Groq API
- 💬 Conversaciones fluidas y naturales
- 🎨 Respuestas en formato HTML
- 🔒 Gestión segura de credenciales

## Requisitos

- Python 3.8+
- Token de Telegram Bot
- Clave de API de Groq

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/NEXOAIGIT/NEXO-AI-4IB0TT3L3CH4T.git
cd NEXO-AI-4IB0TT3L3CH4T
```

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:
```bash
cp .env.example .env
```
Edita el archivo `.env` con tus credenciales:
```
TELEGRAM_TOKEN=tu_token_de_telegram
GROQ_API_KEY=tu_clave_de_api_groq
```

5. Ejecuta el bot:
```bash
python nexo_ai.py
```

## Comandos

- `/start` - Mensaje de bienvenida
- `/help` - Muestra los comandos disponibles
- `/preguntar [texto]` - Haz una pregunta a la IA

## Uso

Puedes interactuar con el bot de dos formas:
- Usando el comando `/preguntar` seguido de tu pregunta
- Enviando un mensaje directamente al bot

## Contribución

¡Las contribuciones son bienvenidas! Si deseas mejorar el proyecto:
1. Haz un fork del repositorio
2. Crea una rama para tu función
3. Realiza tus cambios y haz commit
4. Sube tus cambios y crea un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.

## Soporte

Para soporte, únete a nuestro grupo de Facebook: [NEXO AI Community](https://www.facebook.com/share/g/18zST2GjHn/)

```