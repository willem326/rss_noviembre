import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pytz
from datetime import datetime
from feedgen.feed import FeedGenerator

# URL de la página de noticias
url = 'https://www.emol.com/todas'

# Configurar Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Ejecutar en modo headless (sin ventana visible)
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Cargar la página y obtener el HTML
driver.get(url)
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# Generar el feed RSS
def generar_feed_rss(soup):
    fg = FeedGenerator()
    fg.title('Emol - Todas las noticias')
    fg.link(href=url, rel='alternate')
    fg.description('Feed RSS generado automáticamente desde la página Todas las noticias de Emol')

    article_containers = soup.find_all('li', class_='ContenedorLinkNoticia')
    if not article_containers:
        article_containers = soup.find_all('li', id='ContenedorLinkNoticia')

    for container in article_containers:
        article = container.find('a', id='LinkNoticia')
        if article:
            title = article.get_text(strip=True)
            link = article['href']
            if 'www.emol.com' in link:
                link = 'https://www.emol.com' + link.split('www.emol.com')[-1]
            else:
                link = 'https://www.emol.com' + link

            time_tag = container.find('span', class_='bus_txt_fuente')
            if time_tag:
                time_text = time_tag.get_text(strip=True)
                try:
                    publish_date = datetime.now().strftime('%Y-%m-%d') + ' ' + time_text.split('|')[0].strip()
                    publish_datetime = datetime.strptime(publish_date, '%Y-%m-%d %H:%M')
                    publish_datetime = publish_datetime.replace(tzinfo=pytz.timezone('America/Santiago'))
                except ValueError:
                    publish_datetime = datetime.now(pytz.timezone('America/Santiago'))
            else:
                publish_datetime = datetime.now(pytz.timezone('America/Santiago'))

            description = 'No description available'

            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(description)
            fe.published(publish_datetime)

    rss_feed = fg.rss_str(pretty=True)
    return rss_feed

# Generar y guardar el feed RSS
rss_feed = generar_feed_rss(soup)

if rss_feed:
    # Obtener la ruta del directorio del script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Guardar el feed en la misma carpeta que el script
    output_path = os.path.join(current_directory, 'emol_feed.xml')
    
    with open(output_path, 'wb') as f:
        f.write(rss_feed)
    print(f'Feed RSS generado y guardado como {output_path}')
else:
    print('No se pudo generar el feed RSS.')
