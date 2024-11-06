import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# URL del feed de BioBioChile
biobio_feed_url = "https://www.biobiochile.cl/static/google-news-sitemap.xml"

def obtener_feed_biobio():
    response = requests.get(biobio_feed_url)
    if response.status_code != 200:
        print(f"Error al obtener el feed de BioBioChile: {response.status_code}")
        return None
    
    return response.content

def procesar_feed_biobio(feed_content):
    soup = BeautifulSoup(feed_content, 'xml')
    noticias = []

    for item in soup.find_all('url'):
        titulo = item.find('n:title').text if item.find('n:title') else "Sin título"
        enlace = item.find('loc').text if item.find('loc') else "Sin enlace"
        fecha_publicacion = item.find('n:publication_date').text if item.find('n:publication_date') else "Sin fecha"
        
        # Convertir fecha a formato deseado para <pubDate>
        fecha_publicacion = convertir_fecha_rss(fecha_publicacion)

        noticia = {
            'titulo': titulo,
            'enlace': enlace,
            'descripcion': "No description available",  # Suponemos que no hay descripción directa en el feed
            'fecha_publicacion': fecha_publicacion,
        }
        noticias.append(noticia)
    
    return noticias

def convertir_fecha_rss(fecha):
    # Convierte la fecha del formato '2024-09-09T03:57Z' a un formato RSS estándar 'Wed, 11 Sep 2024 14:01:00 -0443'
    try:
        # Convertimos la fecha recibida en UTC a un objeto datetime
        fecha_dt = datetime.strptime(fecha, '%Y-%m-%dT%H:%M:%SZ')

        # Aplicamos la zona horaria correspondiente (en este caso, asumiendo que el formato final requiere -4 horas)
        chile_tz = pytz.timezone('America/Santiago')  # Ajusta si necesitas otra zona horaria
        fecha_dt = fecha_dt.replace(tzinfo=pytz.UTC).astimezone(chile_tz)

        # Devolvemos la fecha en el formato solicitado
        return fecha_dt.strftime('%a, %d %b %Y %H:%M:%S %z')
    except ValueError:
        return "Fecha inválida"

def generar_rss_biobio(noticias, archivo_salida='biobio_feed.xml'):
    # Comenzar a construir el XML de un feed RSS
    rss_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>BioBioChile - Todas las noticias</title>
    <link>https://www.biobiochile.cl</link>
    <description>Feed RSS generado automáticamente desde BioBioChile</description>
    <generator>python-feedgen</generator>
    <lastBuildDate>{last_build_date}</lastBuildDate>
'''.format(last_build_date=datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z'))

    # Añadir cada noticia como un <item>
    for noticia in noticias:
        rss_content += f'''
    <item>
        <title>{noticia['titulo']}</title>
        <link>{noticia['enlace']}</link>
        <description>{noticia['descripcion']}</description>
        <pubDate>{noticia['fecha_publicacion']}</pubDate>
    </item>
        '''
    
    # Cerrar el canal y el feed RSS
    rss_content += '''
</channel>
</rss>
    '''

    # Obtener la ruta actual del script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Guardar el feed RSS en el mismo directorio donde está el script
    output_path = os.path.join(current_directory, archivo_salida)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rss_content)

    print(f"Archivo RSS {output_path} generado con éxito.")

def main():
    feed_content = obtener_feed_biobio()
    if feed_content:
        noticias = procesar_feed_biobio(feed_content)
        generar_rss_biobio(noticias)

if __name__ == "__main__":
    main()
