import os
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz

# URL del sitemap de El Mostrador
elmostrador_sitemap_url = "https://www.elmostrador.cl/sitemap_news.xml"

# Función para obtener el sitemap de El Mostrador
def obtener_sitemap_elmostrador():
    response = requests.get(elmostrador_sitemap_url)
    if response.status_code != 200:
        print(f"Error al obtener el sitemap de El Mostrador: {response.status_code}")
        return None
    return response.content

# Función para procesar y filtrar las noticias
def procesar_sitemap_elmostrador(sitemap_content):
    soup = BeautifulSoup(sitemap_content, 'xml')
    noticias = []

    for url in soup.find_all('url'):
        loc = url.find('loc').text if url.find('loc') else None
        title = url.find('n:title').text if url.find('n:title') else "Sin título"
        pub_date = url.find('n:publication_date').text if url.find('n:publication_date') else "Sin fecha"

        noticia = {
            'titulo': title,
            'enlace': loc,
            'fecha_publicacion': pub_date
        }
        noticias.append(noticia)

    return noticias

# Función para generar el archivo RSS
def generar_rss_elmostrador(noticias, archivo_salida='elmostrador_feed.xml'):
    fg = FeedGenerator()
    fg.title('El Mostrador - Noticias Recientes')
    fg.link(href=elmostrador_sitemap_url, rel='alternate')
    fg.description('Feed RSS generado automáticamente desde el sitemap de El Mostrador')

    for noticia in noticias:
        fe = fg.add_entry()
        fe.title(noticia['titulo'])
        fe.link(href=noticia['enlace'])
        fe.pubDate(noticia['fecha_publicacion'])

    rss_feed = fg.rss_str(pretty=True)

    # Obtener la ruta actual del script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Guardar el feed RSS en el directorio actual
    output_path = os.path.join(current_directory, archivo_salida)
    
    with open(output_path, 'wb') as f:
        f.write(rss_feed)
    print(f"Archivo RSS generado y guardado como {output_path}")

# Función principal
def main():
    sitemap_content = obtener_sitemap_elmostrador()
    if sitemap_content:
        noticias = procesar_sitemap_elmostrador(sitemap_content)
        if noticias:
            generar_rss_elmostrador(noticias)
        else:
            print("No se encontraron noticias.")
    else:
        print("No se pudo obtener el sitemap de El Mostrador.")

if __name__ == "__main__":
    main()
