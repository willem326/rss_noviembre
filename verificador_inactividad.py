import os
import json
import time
from datetime import datetime, timedelta
import requests
import schedule

# Configuración
noticias_directory = 'noticias/'  # Carpeta donde se almacenan los archivos de noticias
MONITORED_MEDIAS = [

    "Cooperativa.cl", 
    "Diario Financiero Online", 
    "La Tercera", 
    "Publimetro Chile", 
    "The Clinic", 
    "El Desconcierto", 
    "Ex-Ante",
    "CIPER Chile", #acostumbra pasar mas de 12 horas sin publicaciones
    "Radio Agricultura",
    "Chilevisión - Sitemap Noticias",
    "BioBioChile - Todas las noticias", 
    "El Ciudadano - Noticias de Chile", #en la categoria Chile, pasan mas de 12 horas (revisar si se está perdiendo info)
    "CNN Chile - Sitemap Noticias",
    "Emol - Todas las noticias",
    "La Cuarta - Sitemap Noticias",
    "El Mostrador - Noticias Recientes",
    "T13 - Lo Último",
    "Radio Duna",
    "El País"
    
]

# Telegram configuration
TELEGRAM_BOT_TOKEN = '6856314126:AAFmtwNz5ihIRWHT4a7vnFyksM7Av9YVn1Y'  # Token del bot de Telegram
TELEGRAM_CHAT_ID = '186640618'  # ID de chat de Telegram

# Configuración de logs
log_dir = "log"
log_file = os.path.join(log_dir, "verificador_inactividad.log")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def escribir_log(mensaje):
    """Escribir el log al inicio del archivo."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {mensaje}\n"
    contenido = ""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            contenido = f.read()
    with open(log_file, 'w') as f:
        f.write(log_entry + contenido)

# Función para encontrar los archivos JSON modificados en las últimas 10 horas
def find_recent_news_files(directory):
    now = time.time()
    ten_hours_ago = now - (10 * 3600)
    recent_files = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.startswith('noticias_') and file_name.endswith('.json'):
                file_mod_time = os.path.getmtime(file_path)
                if file_mod_time > ten_hours_ago:
                    recent_files.append(file_path)
    escribir_log(f"Archivos recientes encontrados: {len(recent_files)}")
    return recent_files

# Función para extraer la noticia más reciente de cada medio
def find_latest_news_per_medium(files):
    latest_news = {medium: None for medium in MONITORED_MEDIAS}
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            if not isinstance(news_data, list):
                continue
            for article in news_data:
                medium = article.get('medio')
                fecha_publicacion = article.get('fecha_publicacion')
                if medium in MONITORED_MEDIAS and fecha_publicacion:
                    try:
                        fecha_obj = datetime.strptime(fecha_publicacion, "%d de %B del %Y - %H:%M")
                        if latest_news[medium] is None or fecha_obj > latest_news[medium]['fecha_obj']:
                            latest_news[medium] = {'noticia': article, 'fecha_obj': fecha_obj}
                    except ValueError:
                        continue
        except (json.JSONDecodeError, Exception):
            escribir_log(f"Error procesando archivo: {file_path}")
            continue
    escribir_log(f"Noticias más recientes extraídas de {len(files)} archivos.")
    return latest_news

# Función para enviar un mensaje a Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        escribir_log("Mensaje enviado a Telegram con éxito.")
    else:
        escribir_log(f"Error al enviar mensaje a Telegram: {response.status_code} - {response.text}")

# Función principal para buscar noticias y verificar inactividad
def show_latest_news_and_check_inactivity():
    escribir_log("Iniciando verificación de inactividad.")
    recent_files = find_recent_news_files(noticias_directory)
    
    # Si no se encontraron archivos recientes, lo notificamos
    if not recent_files:
        escribir_log("No se encontraron archivos de noticias recientes.")
        send_telegram_message("⚠️ No se encontraron archivos de noticias recientes en las últimas horas.")
        return
    
    latest_news = find_latest_news_per_medium(recent_files)
    medios_inactivos = []
    ahora = datetime.now()

    for medium, info in latest_news.items():
        if info:
            horas_inactivas = (ahora - info['fecha_obj']).total_seconds() / 3600
            escribir_log(f"{medium}: Última noticia hace {horas_inactivas:.2f} horas.")
            if horas_inactivas > 12:
                medios_inactivos.append(f"⚠️ {medium} no presenta noticias hace más de 12 horas.")
        else:
            medios_inactivos.append(f"{medium} no tiene noticias recientes.")
            escribir_log(f"{medium}: Sin noticias recientes.")

    # Si hay medios inactivos, lo notificamos
    if medios_inactivos:
        send_telegram_message("\n".join(medios_inactivos))
        escribir_log(f"Medios inactivos: {', '.join(medios_inactivos)}")
    else:
        # Si no hay medios inactivos, notificamos que todo está bien
        send_telegram_message("✅ Sistema funcionando correctamente, no hay medios inactivos.")
        escribir_log("Todos los medios están activos.")

    escribir_log("Finalizando verificación de inactividad.")
    # Agregar separación al final de la ejecución
    escribir_log("*" * 50)


# Programar la ejecución cada 6 horas
schedule.every(6).hours.do(show_latest_news_and_check_inactivity)
show_latest_news_and_check_inactivity()

# Mantener el script ejecutándose
while True:
    schedule.run_pending()
    time.sleep(1)
