import os
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz

# URL del feed de El Ciudadano
elciudadano_feed_url = "https://www.elciudadano.com/feed"

# Función para obtener el feed de El Ciudadano
def obtener_feed_elciudadano():
    response = requests.get(elciudadano_feed_url)
    if response.status_code != 200:
        print(f"Error al obtener el feed de El Ciudadano: {response.status_code}")
        return None
    return response.content

# Función para procesar y filtrar las noticias que solo pertenezcan a la categoría "Chile"
def procesar_feed_elciudadano(feed_content):
    soup = BeautifulSoup(feed_content, 'xml')
    noticias_chile = []

    for item in soup.find_all('item'):
        # Extraer las categorías
        categorias = item.find_all('category')
        if categorias:
            # Verificar si alguna de las categorías es "Chile"
            categorias_text = [categoria.get_text().lower() for categoria in categorias]
            if "chile" in categorias_text:
                titulo = item.find('title').text if item.find('title') else "Sin título"
                enlace = item.find('link').text if item.find('link') else "Sin enlace"
                fecha_publicacion = item.find('pubDate').text if item.find('pubDate') else "Sin fecha"

                noticia = {
                    'titulo': titulo,
                    'enlace': enlace,
                    'descripcion': item.find('description').text if item.find('description') else "No description available",
                    'fecha_publicacion': fecha_publicacion,
                }
                noticias_chile.append(noticia)
    return noticias_chile

# Función para generar el archivo RSS filtrado
def generar_rss_elciudadano(noticias, archivo_salida='elciudadano_chile_feed.xml'):
    fg = FeedGenerator()
    fg.title('El Ciudadano - Noticias de Chile')
    fg.link(href=elciudadano_feed_url, rel='alternate')
    fg.description('Feed RSS generado automáticamente con noticias de Chile')

    for noticia in noticias:
        fe = fg.add_entry()
        fe.title(noticia['titulo'])
        fe.link(href=noticia['enlace'])
        fe.description(noticia['descripcion'])
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
    feed_content = obtener_feed_elciudadano()
    if feed_content:
        noticias_chile = procesar_feed_elciudadano(feed_content)
        if noticias_chile:
            generar_rss_elciudadano(noticias_chile)
        else:
            print("No se encontraron noticias de la categoría 'Chile'.")
    else:
        print("No se pudo obtener el feed de El Ciudadano.")

if __name__ == "__main__":
    main()
