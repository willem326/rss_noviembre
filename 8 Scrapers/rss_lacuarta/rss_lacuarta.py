import os
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# URL del sitemap de La Cuarta
lacuarta_sitemap_url = "https://www.lacuarta.com/arc/outboundfeeds/news-sitemap/?outputType=xml"

# Función para obtener el sitemap de La Cuarta
def obtener_sitemap_lacuarta():
    response = requests.get(lacuarta_sitemap_url)
    if response.status_code != 200:
        print(f"Error al obtener el sitemap de La Cuarta: {response.status_code}")
        return None
    return response.content

# Función para extraer el título de una página dada la URL
def obtener_titulo_noticia(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error al obtener la página: {response.status_code}")
            return "Sin título"
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Suponiendo que el título de las noticias está en una etiqueta <h1>
        title_tag = soup.find('h1')
        if title_tag:
            return title_tag.get_text(strip=True)
        else:
            return "Sin título"
    except Exception as e:
        print(f"Error al obtener el título de {url}: {e}")
        return "Sin título"

# Función para procesar el sitemap de La Cuarta y extraer los enlaces y fechas de publicación
def procesar_sitemap_lacuarta(sitemap_content):
    soup = BeautifulSoup(sitemap_content, 'xml')
    noticias = []

    for url in soup.find_all('url'):
        link = url.find('loc').text if url.find('loc') else "Sin enlace"
        fecha_publicacion = url.find('lastmod').text if url.find('lastmod') else "Sin fecha"
        
        # Obtener el título de la página
        titulo = obtener_titulo_noticia(link)

        noticia = {
            'titulo': titulo,  # Usamos el título extraído
            'enlace': link,
            'fecha_publicacion': fecha_publicacion,
            'descripcion': ''  # Dejar la descripción vacía
        }
        noticias.append(noticia)

    return noticias

# Función para generar el archivo RSS
def generar_rss_lacuarta(noticias, archivo_salida='lacuarta_feed.xml'):
    fg = FeedGenerator()
    fg.title('La Cuarta - Sitemap Noticias')
    fg.link(href=lacuarta_sitemap_url, rel='alternate')
    fg.description('Feed RSS generado automáticamente desde el sitemap de La Cuarta')

    for noticia in noticias:
        fe = fg.add_entry()
        fe.title(noticia['titulo'])  # Usamos el título extraído
        fe.link(href=noticia['enlace'])
        fe.description(noticia['descripcion'])  # Dejar vacío
        fe.pubDate(noticia['fecha_publicacion'])

    rss_feed = fg.rss_str(pretty=True)

    # Obtener la ruta actual del script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Guardar el feed RSS en la misma carpeta donde está el script
    output_path = os.path.join(current_directory, archivo_salida)
    
    with open(output_path, 'wb') as f:
        f.write(rss_feed)
    print(f"Archivo RSS generado y guardado como {output_path}")

# Función principal
def main():
    sitemap_content = obtener_sitemap_lacuarta()
    if sitemap_content:
        noticias = procesar_sitemap_lacuarta(sitemap_content)
        if noticias:
            generar_rss_lacuarta(noticias)
        else:
            print("No se encontraron noticias.")
    else:
        print("No se pudo obtener el sitemap de La Cuarta.")

if __name__ == "__main__":
    main()
