import feedparser
import json
from datetime import datetime
import pytz
import os
import hashlib
import requests
from io import BytesIO
import subprocess  # Para ejecutar scrapers_especiales

# URLs de los RSS feeds que comparten formato y no requieren un proceso aparte
rss_feeds = [
    'https://www.cooperativa.cl/noticias/site/tax/port/all/rss_3___1.xml',
    'https://www.df.cl/noticias/site/list/port/rss.xml',
    'https://www.latercera.com/arcio/rss/',
    'https://www.publimetro.cl/arc/outboundfeeds/rss/?outputType=xml',
    'https://www.theclinic.cl/feed',
    'https://eldesconcierto.cl/feed',
    'https://www.ex-ante.cl/feed',
    'https://www.ciperchile.cl/feed',
    'https://www.radioagricultura.cl/feed',
    'https://www.duna.cl/feed',
    'https://feeds.elpais.com/mrss-s/list/ep/site/elpais.com/section/chile/subsection/actualidad'
]

# Zona horaria de Chile
chile_tz = pytz.timezone('America/Santiago')

# Directorio base donde se almacenan los archivos XML de scrapers especiales
scrapers_base_dir = './8 scrapers/'

# Función para crear la estructura de carpetas
def create_directory_structure(base_dir):
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    current_date = datetime.now(chile_tz)
    month_str = current_date.strftime('%B')
    today_str = current_date.strftime('%d-%m-%Y')
    monthly_dir = os.path.join(base_dir, month_str)
    if not os.path.exists(monthly_dir):
        os.makedirs(monthly_dir)
    daily_dir = os.path.join(monthly_dir, today_str)
    if not os.path.exists(daily_dir):
        os.makedirs(daily_dir)
    return daily_dir

# Función para generar un identificador único
def generate_id(article):
    hash_input = (article['titulo'] + article['contenido']).encode('utf-8')
    return hashlib.md5(hash_input).hexdigest()

# Función para cargar los identificadores guardados
def load_saved_links(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

# Función para guardar los identificadores nuevos
def save_new_links(filename, links):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(list(links), f)

# Ejecutar scrapers especiales
def ejecutar_scrapers_especiales():
    try:
        print("Ejecutando scrapers especiales...")
        result = subprocess.run(['python', 'scrapers_especiales.py'], check=True)
        print(f"scrapers_especiales.py terminado con código de salida {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar scrapers_especiales.py: {e}")
        return

# Función para buscar todos los archivos XML en el directorio de scrapers (de manera recursiva)
def buscar_archivos_xml(scrapers_base_dir):
    xml_files = []
    for root, dirs, files in os.walk(scrapers_base_dir):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                xml_files.append(file_path)
                print(f"Encontrado archivo XML: {file_path}")
    return xml_files

# Función para parsear archivos XML locales generados por scrapers especiales
def parse_local_xml_files(xml_files):
    all_articles = []
    for file_path in xml_files:
        try:
            print(f"Parseando archivo XML local: {file_path}")
            
            # Abrimos el archivo XML de forma correcta
            with open(file_path, 'r', encoding='utf-8') as xml_file:
                feed = feedparser.parse(xml_file.read())  # Parseamos el contenido como cadena de texto

                # Verificar que feedparser haya parseado correctamente el XML
                if not feed or 'entries' not in feed or feed.entries is None:
                    print(f"Error: No se pudo parsear correctamente el archivo XML {file_path}")
                    continue

                # Procesar cada entrada en el feed
                for entry in feed.entries:
                    published_time = entry.published_parsed
                    if published_time:
                        published_datetime = datetime(*published_time[:6], tzinfo=pytz.utc).astimezone(chile_tz)
                        formatted_date = published_datetime.strftime('%d de %B del %Y - %H:%M')
                    else:
                        formatted_date = "Sin fecha"

                    article = {
                        'medio': feed.feed.title if 'title' in feed.feed else "Sin medio",
                        'titulo': entry.title if 'title' in entry else "Sin título",
                        'contenido': entry.description if 'description' in entry else "Sin contenido",
                        'fecha_publicacion': formatted_date,
                        'enlace': entry.link if 'link' in entry else "Sin enlace"
                    }
                    all_articles.append(article)
        except Exception as e:
            print(f"Error al procesar el archivo XML {file_path}: {e}")
    return all_articles

# Función para obtener y parsear los feeds RSS desde URLs
def fetch_rss_feeds(rss_feeds):
    all_articles = []
    for feed_url in rss_feeds:
        try:
            # Intentar descargar el contenido de la URL
            response = requests.get(feed_url)
            content_type = response.headers.get('Content-Type', '')
            
            # Comprobar si el contenido es un archivo (por ejemplo, application/octet-stream)
            if 'application/octet-stream' in content_type or response.headers.get('Content-Disposition'):
                # Usar el contenido descargado para parsear el XML
                feed = feedparser.parse(BytesIO(response.content))
            else:
                # Si es un feed normal, parsearlo directamente desde la URL
                feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                # Convertir la fecha de publicación a la zona horaria de Chile
                published_time = entry.published_parsed
                published_datetime = datetime(*published_time[:6], tzinfo=pytz.utc).astimezone(chile_tz)
                formatted_date = published_datetime.strftime('%d de %B del %Y - %H:%M')
                
                #Ajustar nombre de El País
                medio = "El País" if "elpais.com" in feed_url else feed.feed.title

                article = {
                    'medio': medio,
                    'titulo': entry.title,
                    'contenido': entry.description,
                    'fecha_publicacion': formatted_date,
                    'enlace': entry.link
                }
                all_articles.append(article)

        except Exception as e:
            print(f"Error al procesar el feed {feed_url}: {e}")

    return all_articles

# Función para guardar las noticias nuevas
def save_articles(articles, daily_dir, saved_links, identificadores_guardados_file):
    new_articles = []
    for article in articles:
        article_id = generate_id(article)
        if article_id not in saved_links:
            new_articles.append(article)
            saved_links.add(article_id)
    
    if new_articles:
        formatted_time = datetime.now(chile_tz).strftime('%H-%M-%S')
        daily_file = os.path.join(daily_dir, f'noticias_{formatted_time}.json')
        with open(daily_file, 'w', encoding='utf-8') as f:
            json.dump(new_articles, f, ensure_ascii=False, indent=4)
        
        # Actualizar el archivo de identificadores guardados
        save_new_links(identificadores_guardados_file, saved_links)
        print(f"Noticias guardadas en {daily_file}")
    else:
        print("No hay noticias nuevas.")

# Función principal para el procesamiento
def main():
    base_dir = './noticias'
    daily_dir = create_directory_structure(base_dir)
    
    identificadores_guardados_file = os.path.join(base_dir, 'identificadores_guardados.json')
    saved_links = load_saved_links(identificadores_guardados_file)
    
    # Ejecutar scrapers especiales antes de procesar los feeds RSS
    ejecutar_scrapers_especiales()
    
    # Buscar todos los archivos XML generados por los scrapers en 8 scrapers
    xml_files = buscar_archivos_xml(scrapers_base_dir)
    
    # Parsear los archivos XML locales
    articles_from_xml = parse_local_xml_files(xml_files)
    
    # Parsear los feeds RSS desde URLs
    articles_from_feeds = fetch_rss_feeds(rss_feeds)
    
    # Combinar todos los artículos
    all_articles = articles_from_xml + articles_from_feeds
    
    # Guardar todas las noticias nuevas
    save_articles(all_articles, daily_dir, saved_links, identificadores_guardados_file)

if __name__ == "__main__":
    main()
