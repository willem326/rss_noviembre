import os
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# URL del sitemap de Chilevisión
chilevision_sitemap_url = "https://www.chilevision.cl/chilevision/site/sitemap_news_chvn.xml"

# Función para obtener el sitemap de Chilevisión
def obtener_sitemap_chilevision():
    response = requests.get(chilevision_sitemap_url)
    if response.status_code != 200:
        print(f"Error al obtener el sitemap de Chilevisión: {response.status_code}")
        return None
    return response.content

# Función para procesar el sitemap de Chilevisión y extraer los enlaces, títulos y fechas de publicación
def procesar_sitemap_chilevision(sitemap_content):
    soup = BeautifulSoup(sitemap_content, 'xml')
    noticias = []

    for url in soup.find_all('url'):
        link = url.find('loc').text if url.find('loc') else "Sin enlace"
        fecha_publicacion = url.find('news:publication_date').text if url.find('news:publication_date') else "Sin fecha"
        titulo = url.find('news:title').text if url.find('news:title') else "Sin título"
        
        noticia = {
            'titulo': titulo,  # Usamos el título extraído
            'enlace': link,
            'fecha_publicacion': fecha_publicacion,
            'descripcion': ''  # Dejar la descripción vacía
        }
        noticias.append(noticia)

    return noticias

# Función para generar el archivo RSS
def generar_rss_chilevision(noticias, archivo_salida='chilevision_feed.xml'):
    fg = FeedGenerator()
    fg.title('Chilevisión - Sitemap Noticias')
    fg.link(href=chilevision_sitemap_url, rel='alternate')
    fg.description('Feed RSS generado automáticamente desde el sitemap de Chilevisión')

    for noticia in noticias:
        fe = fg.add_entry()
        fe.title(noticia['titulo'])
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
    sitemap_content = obtener_sitemap_chilevision()
    if sitemap_content:
        noticias = procesar_sitemap_chilevision(sitemap_content)
        if noticias:
            generar_rss_chilevision(noticias)
        else:
            print("No se encontraron noticias.")
    else:
        print("No se pudo obtener el sitemap de Chilevisión.")

if __name__ == "__main__":
    main()
