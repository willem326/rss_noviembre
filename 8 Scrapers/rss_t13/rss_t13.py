import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz  # Para manejar la zona horaria
import os  # Para manejar la ruta de guardado del XML

# Definir la zona horaria de Chile
chile_tz = pytz.timezone('America/Santiago')

# URL de la sección "Lo Último" de T13
url = 'https://www.t13.cl/lo-ultimo'

# Realizar la petición HTTP
response = requests.get(url)

# Verificar si la petición fue exitosa
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Crear el generador de feeds
    fg = FeedGenerator()
    fg.title('T13 - Lo Último')
    fg.link(href='https://www.t13.cl/lo-ultimo')
    fg.description('Feed RSS generado automáticamente desde la sección Lo Último de T13')
    fg.language('es')
    fg.generator('python-feedgen')

    # Buscar las noticias en el contenedor principal
    noticias = soup.find_all('a', class_='item-article')

    for noticia in noticias:
        # Extraer el enlace (href)
        enlace = noticia.get('href', None)
        if enlace and not enlace.startswith('http'):
            enlace = 'https://www.t13.cl' + enlace  # Completar con el dominio si es relativo

        # Extraer el título
        titulo_element = noticia.find('div', class_='item-article__info__title')
        titulo = titulo_element.text.strip() if titulo_element else "Sin título"
        
        # Extraer la hora de publicación (por ejemplo, "04:32")
        hora_element = noticia.find('time', class_='item-article__time')
        hora_publicacion = hora_element.text.strip() if hora_element else "00:00"
        
        # Obtener la fecha actual
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        # Combinar la fecha actual con la hora extraída
        fecha_hora_str = f"{fecha_actual} {hora_publicacion}:00"
        
        # Convertir la cadena de fecha y hora a un objeto datetime
        fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M:%S')
        
        # Asignar la zona horaria de Chile
        fecha_hora = chile_tz.localize(fecha_hora)
        
        # Añadir el artículo al feed
        fe = fg.add_entry()
        fe.title(titulo)
        fe.link(href=enlace)
        fe.pubDate(fecha_hora)  # Ahora estamos pasando un objeto datetime con zona horaria
        fe.description('')  # Dejar la descripción vacía

    # Obtener la ruta de la carpeta del script actual
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Guardar el archivo XML en la misma carpeta que el script
    fg.rss_file(os.path.join(script_dir, 't13_feed.xml'), pretty=True)
    print(f"Feed generado y guardado en {os.path.join(script_dir, 't13_feed.xml')}")
    
else:
    print(f"Error al acceder a la página: {response.status_code}")
