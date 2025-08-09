#!/usr/bin/env python3
"""
Bot de Telegram con IA - Versión Mejorada
Descripción: Bot que responde preguntas usando Groq API con respuestas HTML y amigables
Autor: [Tu Nombre]
Versión: 1.3.0
"""

# Importaciones necesarias
import os
import logging
import asyncio
import webbrowser
import time
import re
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de logging (explicar para qué sirve)
# El logging nos permite registrar eventos y errores que ocurren durante la ejecución del bot.
# Esto es útil para depurar problemas y monitorear el funcionamiento del bot.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variables de configuración (explicar cada una)
# TELEGRAM_TOKEN: Token de autenticación del bot de Telegram obtenido desde @BotFather.
# Se obtiene de las variables de entorno para no exponerlo en el código.
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# GROQ_API_KEY: Clave de API para acceder a los servicios de Groq.
# Se obtiene de las variables de entorno para no exponerla en el código.
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Variable para controlar si ya se abrió Facebook
facebook_opened = False

# Inicializar clientes (explicar qué hace cada uno)
# application: Aplicación de Telegram que interactuará con la API de Telegram.
# Se inicializará después en la función main().
application = None

# groq_client: Cliente de Groq que interactuará con la API de Groq.
# Se inicializará después en la función main().
groq_client = None

# Función para convertir formato Markdown a HTML
def markdown_to_html(text: str) -> str:
    """Convierte texto con formato Markdown a formato HTML válido para Telegram"""
    # Reemplazar **texto** por <b>texto</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Reemplazar *texto* por <i>texto</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Reemplazar `texto` por <code>texto</code>
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Reemplazar ```texto``` por <pre>texto</pre>
    text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)
    
    return text

# Función para abrir Facebook después de 20 segundos
async def open_facebook_after_delay():
    """Abre la página de Facebook después de 20 segundos de ejecución"""
    global facebook_opened
    await asyncio.sleep(20)  # Esperar 20 segundos
    
    if not facebook_opened:
        try:
            # Abrir la página de Facebook en el navegador predeterminado
            webbrowser.open("https://www.facebook.com/NEXOAICHATBOT")
            facebook_opened = True
            logger.info("Página de Facebook abierta correctamente")
        except Exception as e:
            logger.error(f"Error al abrir Facebook: {e}")

# Función principal del bot (explicar flujo)
async def main():
    """Función principal que inicia el bot"""
    # 1. Verificar tokens
    # Comprobamos si los tokens necesarios están configurados correctamente.
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        logger.error("Tokens no configurados. Por favor, crea un archivo .env con TELEGRAM_TOKEN y GROQ_API_KEY.")
        return
    
    # 2. Inicializar clientes
    # Inicializamos la aplicación de Telegram usando el token proporcionado.
    global application, groq_client
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Inicializamos el cliente de Groq usando la clave de API proporcionada.
    groq_client = Groq(api_key=GROQ_API_KEY)
    
    # 3. Configurar manejadores
    # Registramos el manejador para el comando /start.
    application.add_handler(CommandHandler("start", start_command))
    
    # Registramos el manejador para el comando /help.
    application.add_handler(CommandHandler("help", help_command))
    
    # Registramos el manejador para el comando /preguntar.
    application.add_handler(CommandHandler("preguntar", ask_command))
    
    # Registramos el manejador para mensajes de texto que no son comandos.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Registramos el manejador de errores.
    application.add_error_handler(error_handler)
    
    # 4. Iniciar el bot
    # Iniciamos el bot y lo ponemos a escuchar mensajes.
    logger.info("Bot iniciado correctamente")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Iniciar la tarea para abrir Facebook después de 20 segundos
    asyncio.create_task(open_facebook_after_delay())
    
    # Mantenemos el bot en ejecución
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Detenemos el bot de manera controlada
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

# Funciones de comandos (cada una con comentarios detallados)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start - Envía un mensaje de bienvenida al usuario"""
    # Obtenemos el nombre del usuario que envió el comando.
    user_name = update.effective_user.first_name
    
    # Creamos un mensaje de bienvenida personalizado con formato HTML.
    welcome_message = f"""
    <b>¡Hola, {user_name}! 👋</b>
    
    ¡Qué bueno que estás aquí! Soy NEXO AI, tu amigo inteligente que está aquí para ayudarte con lo que necesites. 😊
    
    Puedes preguntarme lo que sea, desde dudas hasta consejos. Solo usa el comando <b>/preguntar</b> seguido de tu pregunta o simplemente escríbeme directamente como a un amigo.
    
    ¿Qué te gustaría saber hoy? 🤔
    """
    
    # Enviamos el mensaje de bienvenida al usuario.
    await update.message.reply_text(welcome_message, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /help - Muestra una lista de comandos disponibles"""
    # Creamos un mensaje con la lista de comandos disponibles con formato HTML.
    help_message = """
    <b>🤖 Comandos Disponibles:</b>
    
    <b>/start</b> - Mensaje de bienvenida
    <b>/help</b> - Muestra esta ayuda
    <b>/preguntar [texto]</b> - Haz una pregunta a la IA
    
    También puedes simplemente enviarme cualquier mensaje de texto y te responderé como tu amigo inteligente. 😊
    """
    
    # Enviamos el mensaje de ayuda al usuario.
    await update.message.reply_text(help_message, parse_mode='HTML')

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /preguntar - Envía la pregunta del usuario a la IA y muestra la respuesta"""
    # Verificamos si el usuario proporcionó una pregunta después del comando.
    if not context.args:
        # Si no hay argumentos, informamos al usuario cómo usar el comando.
        await update.message.reply_text("Por favor, usa el comando de esta manera: <b>/preguntar [tu pregunta]</b>", parse_mode='HTML')
        return
    
    # Unimos todos los argumentos para formar la pregunta completa.
    question = ' '.join(context.args)
    
    # Enviamos un mensaje indicando que estamos procesando la pregunta.
    processing_message = await update.message.reply_text("Procesando tu pregunta... 🤔", parse_mode='HTML')
    
    try:
        # Obtenemos la respuesta de la IA usando la función get_ai_response.
        response = await get_ai_response(question, update.effective_user.first_name)
        
        # Editamos el mensaje de procesamiento con la respuesta obtenida.
        await processing_message.edit_text(response, parse_mode='HTML')
    except Exception as e:
        # Si ocurre un error, lo registramos y enviamos un mensaje de error al usuario.
        logger.error(f"Error al procesar la pregunta: {e}")
        await processing_message.edit_text("Lo siento, ocurrió un error al procesar tu pregunta. Por favor, inténtalo de nuevo más tarde. 😔", parse_mode='HTML')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto - Envía el mensaje del usuario a la IA y muestra la respuesta"""
    # Obtenemos el texto del mensaje del usuario.
    user_message = update.message.text
    
    # Enviamos un mensaje indicando que estamos procesando la pregunta.
    processing_message = await update.message.reply_text("Procesando tu mensaje... 🤔", parse_mode='HTML')
    
    try:
        # Obtenemos la respuesta de la IA usando la función get_ai_response.
        response = await get_ai_response(user_message, update.effective_user.first_name)
        
        # Editamos el mensaje de procesamiento con la respuesta obtenida.
        await processing_message.edit_text(response, parse_mode='HTML')
    except Exception as e:
        # Si ocurre un error, lo registramos y enviamos un mensaje de error al usuario.
        logger.error(f"Error al procesar el mensaje: {e}")
        await processing_message.edit_text("Lo siento, ocurrió un error al procesar tu mensaje. Por favor, inténtalo de nuevo más tarde. 😔", parse_mode='HTML')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja errores - Registra el error y notifica al desarrollador"""
    # Registramos el error con información detallada.
    logger.error(f"Update {update} caused error {context.error}")
    
    # Si hay una actualización disponible, enviamos un mensaje de error al usuario.
    if update and update.effective_message:
        await update.effective_message.reply_text("Lo siento, ocurrió un error inesperado. Por favor, inténtalo de nuevo más tarde. 😔", parse_mode='HTML')

# Función auxiliar para IA (explicar cómo funciona)
async def get_ai_response(question: str, user_name: str) -> str:
    """Obtiene respuesta de la IA usando Groq API con formato HTML y tono amigable"""
    try:
        # Creamos el prompt para la IA, incluyendo la pregunta del usuario y pidiendo un tono amigable.
        # El modelo que usaremos es 'llama-3.3-70b-versatile' que es el reemplazo recomendado
        # para el modelo 'mixtral-8x7b-32768' que ha sido deprecado.
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    Eres NEXO AI, un asistente conversacional inteligente y cercano. Tu objetivo es mantener conversaciones naturales y fluidas con los usuarios.
                    
                    INSTRUCCIONES IMPORTANTES:
                    
                    1. ANÁLISIS CONVERSACIONAL:
                       - Analiza cuidadosamente el mensaje del usuario antes de responder.
                       - Identifica la intención, el contexto y el tono emocional.
                       - Detecta si es una pregunta, una afirmación, un saludo o una conversación continua.
                    
                    2. RESPUESTAS NATURALES Y CONTEXTUALES:
                       - NO INICIES CADA RESPUESTA CON "HOLA" o saludos similares.
                       - Responde de forma directa y natural, como lo haría un humano en una conversación real.
                       - Adapta tu tono según el contexto: más formal para preguntas técnicas, más relajado para conversaciones casuales.
                       - Mantén coherencia con el historial de la conversación.
                    
                    3. CONEXIÓN PERSONAL:
                       - Usa el nombre del usuario ({user_name}) de manera natural, no forzada.
                       - Demuestra empatía y comprensión emocional.
                       - Haz preguntas de seguimiento cuando sea apropiado para mantener la conversación.
                    
                    4. FORMATO HTML VÁLIDO PARA TELEGRAM:
                       - Usa EXCLUSIVAMENTE etiquetas HTML válidas para Telegram:
                       - Usa <b>texto</b> para resaltar palabras clave importantes (NUNCA uses **texto**).
                       - Usa <i>texto</i> para énfasis sutil (NUNCA uses *texto*).
                       - Usa <code>texto</code> para términos técnicos o comandos (NUNCA uses `texto`).
                       - Usa <pre>texto</pre> solo para bloques de código largos (NUNCA uses ```texto```).
                       - Usa <a href='URL'>texto</a> para enlaces.
                       - Estructura con saltos de línea para mejorar la legibilidad.
                    
                    5. EXPRESIVIDAD:
                       - Usa emojis de manera estratégica y moderada (máximo 2-3 por respuesta).
                       - Varía tu vocabulario para evitar repeticiones.
                       - Sé conciso pero completo en tus respuestas.
                    
                    6. EVITA:
                       - Saludos repetitivos en cada respuesta.
                       - Respuestas genéricas o superficiales.
                       - Usar asteriscos (*) o cualquier formato Markdown para texto.
                       - Respuestas demasiado largas o técnicas sin ser solicitadas.
                    
                    7. OBJETIVO FINAL:
                       - Proporcionar valor real en cada interacción.
                       - Crear una experiencia conversacional agradable y útil.
                       - Hacer que el usuario sienta que está hablando con un amigo inteligente, no con un robot.
                    """
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            model="llama-3.3-70b-versatile",  # Modelo de IA a utilizar
            temperature=0.8,  # Controla la creatividad de las respuestas (0.0 a 1.0)
            max_tokens=1000,  # Longitud máxima de la respuesta
            top_p=1.0,  # Controla la diversidad de las respuestas
            stop=None,  # No hay condición de parada específica
            stream=False  # No usamos streaming para la respuesta
        )
        
        # Extraemos el contenido de la respuesta de la IA.
        response = chat_completion.choices[0].message.content
        
        # Convertimos cualquier formato Markdown a HTML antes de devolver la respuesta.
        response = markdown_to_html(response)
        
        return response
    except Exception as e:
        # Si ocurre un error al llamar a la API de Groq, lo registramos y devolvemos un mensaje de error.
        logger.error(f"Error al llamar a la API de Groq: {e}")
        return f"<b>Lo siento, {user_name}</b> 😔\n\nNo pude obtener una respuesta en este momento. Por favor, inténtalo de nuevo más tarde."

# Punto de entrada (explicar cómo se ejecuta el script)
if __name__ == '__main__':
    # Este bloque se ejecuta cuando el script se ejecuta directamente (no cuando se importa como módulo).
    # Ejecutamos la función main() de manera asíncrona.
    asyncio.run(main())