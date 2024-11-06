import schedule
import time
import subprocess
import os
import json
import requests
import hashlib
from datetime import datetime

# Token del bot de Telegram y ID del grupo
TELEGRAM_BOT_TOKEN = '6856314126:AAFmtwNz5ihIRWHT4a7vnFyksM7Av9YVn1Y'

# Archivo de identificadores de noticias enviadas
enviados_guardados_file = 'identificadores_enviados.json'

# Directorio y archivo de log
log_dir = './log/'
log_file = os.path.join(log_dir, 'varys.log')

# Crear el directorio de log si no existe
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def log_message(message, add_separator=False):
    """Función que imprime un mensaje en consola y lo registra en el log, con opción de agregar un separador."""
    print(message)  # Mantiene los prints originales
    
    # Leer el contenido actual del log
    log_content = ""
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
    
    # Preparar la entrada de log con timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {message}\n"
    
    # Si se requiere agregar un separador entre ciclos
    if add_separator:
        log_entry = f"\n--- Nuevo ciclo ---\n{log_entry}"
    
    # Escribir el nuevo log al principio y luego el contenido anterior
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(log_entry + log_content)

# Función para generar un identificador único usando título y enlace
def generate_id(article):
    hash_input = (article['titulo'] + article['enlace']).encode('utf-8')
    return hashlib.md5(hash_input).hexdigest()

# Función para cargar los identificadores guardados
def load_saved_links(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return set(json.load(f))  # Retornamos un set de identificadores
    return set()

# Función para guardar los identificadores nuevos
def save_new_links(filename, links):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(list(links), f)  # Guardamos la lista de identificadores

# Función para ejecutar los scripts de obtención y filtrado de noticias
def execute_scripts():
    log_message("Iniciando ciclo de ejecución de Varys...", add_separator=True)
    
    try:
        log_message("Ejecutando rss3.py...")
        # Ejecutar rss3.py
        result = subprocess.run(['python', 'rss3.py'], check=True)
        log_message(f"rss3.py terminado con código de salida {result.returncode}")
    except subprocess.CalledProcessError as e:
        log_message(f"Error al ejecutar rss3.py: {e}")
        return

    try:
        log_message("Ejecutando buscador2.py...")
        result = subprocess.run(['python', 'buscador2.py'], check=True)
        log_message(f"buscador2.py terminado con código de salida {result.returncode}")
    except subprocess.CalledProcessError as e:
        log_message(f"Error al ejecutar buscador2.py: {e}")
        return

    # Obtener el archivo JSON más reciente generado por buscador2.py
    json_directory = '.'  # Directorio actual
    log_message(f"Buscando archivos JSON en el directorio: {json_directory}")
    exclude_dirs = {'.venv', '.git'}  # Set of directories to ignore
    for root, dirs, files in os.walk(json_directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for name in files:
            if name.startswith('noticias_filtradas_') and name.endswith('.json'):
                log_message(f"Archivo relevante encontrado: {name}")

    recent_files = sorted(
        [os.path.join(root, name)
         for root, dirs, files in os.walk(json_directory)
         for name in files if name.startswith('noticias_filtradas_') and name.endswith('.json')],
        key=lambda x: os.path.getmtime(x), reverse=True
    )

    if recent_files:
        latest_file = recent_files[0]
        log_message(f"Último archivo JSON encontrado: {latest_file}")
        with open(latest_file, 'r', encoding='utf-8') as f:
            news = json.load(f)
            f.close()  # Asegurarse de cerrar el archivo antes de eliminarlo
            if news:
                log_message(f"{len(news)} noticias encontradas. Filtrando noticias no enviadas...")
                # Filtrar y enviar las noticias no enviadas a Telegram
                send_news_to_users(news)
                # Ejecutar el script para archivar las noticias antes de borrar
                archive_news(latest_file)
                # Eliminar archivos JSON de noticias filtradas
                delete_old_json_files(recent_files)
            else:
                log_message("No hay noticias nuevas para enviar.")
    else:
        log_message("No se encontraron archivos JSON recientes.")

# Función para enviar noticias a los usuarios
def send_news_to_users(news):
    saved_links = load_saved_links(enviados_guardados_file)  # Cargamos los identificadores previos
    new_links = set()

    for article in news:
        article_id = generate_id(article)  # Generamos el identificador basado en título y enlace

        # Verificamos si el identificador ya fue guardado
        if article_id in saved_links:
            log_message(f"El artículo '{article['titulo']}' ya fue enviado. No se reenviará.")
            continue  # Si el ID ya existe, no enviar de nuevo

        # Enviar la noticia a todos los usuarios en la lista 'usuarios_destino'
        for user_id in article.get('usuarios_destino', []):
            # (versión con contenido de resumen): 
            # message = f"**{article['medio']}**\n*{article['titulo']}*\n{article['contenido']}\n[Leer más]({article['enlace']})"

            # versión sin contenido de resumen
            message = f"**{article['medio']}**\n*{article['titulo']}*\n[Leer más]({article['enlace']})"

            send_telegram_message(user_id, message)
            new_links.add(article_id)  # Agregamos el identificador a la lista de enviados

    if new_links:
        # Actualizamos el archivo de identificadores guardados
        saved_links.update(new_links)  # Actualizamos el set con los nuevos IDs
        save_new_links(enviados_guardados_file, saved_links)  # Guardamos la lista actualizada
        log_message("Noticias enviadas y guardadas.")
    else:
        log_message("No hay noticias nuevas para enviar.")

# Función para enviar un mensaje a Telegram
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        log_message(f"Mensaje enviado a Telegram al usuario {chat_id} con éxito.")
    else:
        log_message(f"Error al enviar mensaje: {response.status_code} - {response.text}")

# Función para ejecutar el script que archivará las noticias filtradas en el log mensual
def archive_news(noticias_filtradas_file):
    try:
        log_message("Ejecutando script para archivar noticias filtradas...")
        result = subprocess.run(['python', 'archivar_noticias.py', noticias_filtradas_file], check=True)
        log_message(f"Script de archivo ejecutado con éxito. Código de salida: {result.returncode}")
    except subprocess.CalledProcessError as e:
        log_message(f"Error al ejecutar el script de archivo: {e}")

# Función para eliminar los archivos JSON antiguos
def delete_old_json_files(files):
    for file in files:
        try:
            os.remove(file)
            log_message(f"Archivo {file} eliminado.")
        except OSError as e:
            log_message(f"Error al eliminar el archivo {file}: {e}")

# Configurar la ejecución periódica cada 5 minutos
schedule.every(5).minutes.do(execute_scripts)

log_message("Iniciando el planificador...", add_separator=True)

# Ejecutar la primera vez inmediatamente
execute_scripts()

# Ejecutar el planificador
while True:
    schedule.run_pending()
    time.sleep(1)

