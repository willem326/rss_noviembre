import os
from feedgen.feed import FeedGenerator
import feedparser

# Obtener la ruta actual del script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Ruta del archivo del feed original
input_feed_path = os.path.join(current_directory, 'emol_feed.xml')

# Cargar el feed RSS existente
feed = feedparser.parse(input_feed_path)

# Generar un nuevo feed RSS
fg = FeedGenerator()
fg.title(feed.feed.title)
fg.link(href=feed.feed.link, rel='alternate')
fg.description(feed.feed.description)

# Usar un conjunto para evitar duplicados
processed_titles = set()

# Procesar cada entrada del feed existente
for entry in feed.entries:
    title = entry.title
    link = entry.link
    summary = entry.summary if 'summary' in entry else ''
    
    # Extraer la hora de publicación del feed original como string
    publish_datetime_str = entry.published

    # Verificar si el título ya fue procesado
    if title in processed_titles:
        continue
    processed_titles.add(title)

    fe = fg.add_entry()
    fe.title(title)
    fe.link(href=link)
    fe.description(summary)
    fe.published(publish_datetime_str)

# Guardar el nuevo feed RSS sin duplicados en el mismo archivo
output_feed_path = os.path.join(current_directory, 'emol_feed.xml')

rss_feed = fg.rss_str(pretty=True)
with open(output_feed_path, 'wb') as f:
    f.write(rss_feed)

print(f'Feed RSS sin duplicados generado y guardado como {output_feed_path}')
