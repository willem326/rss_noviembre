import os
import json
from datetime import datetime

# Directorio donde se guardarán los logs
log_dir = './log/'

# Archivo de clientes con términos de búsqueda
clientes_file = 'clientes.json'

# Función para cargar los clientes y obtener un diccionario con sus nombres
def load_clients(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        clientes_data = json.load(f)
    
    # Crear un diccionario para buscar nombres por telegram_id
    clientes_dict = {cliente['telegram_id']: cliente['nombre'] for cliente in clientes_data['usuarios']}
    return clientes_dict

# Función para archivar las noticias filtradas
def archivar_noticias(noticias_filtradas_file):
    # Crear el directorio de logs si no existe
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Obtener la fecha actual para determinar el archivo mensual
    now = datetime.now()
    mes_actual = now.strftime('%Y-%m')
    log_filename = f'noticias_archivadas_{mes_actual}.json'
    log_filepath = os.path.join(log_dir, log_filename)

    # Cargar las noticias filtradas
    with open(noticias_filtradas_file, 'r', encoding='utf-8') as f:
        noticias_filtradas = json.load(f)

    # Cargar el archivo de clientes para obtener los nombres de los usuarios
    clientes_dict = load_clients(clientes_file)

    # Añadir el ID y nombre del cliente a cada noticia
    for article in noticias_filtradas:
        # Si la noticia tiene una lista de 'usuarios_destino', añadir los nombres correspondientes
        if 'usuarios_destino' in article:
            # Crear una lista de clientes destino como una cadena para compactarlo
            clientes = [f'{{"ID": "{user_id}", "nombre": "{clientes_dict.get(user_id, "Desconocido")}"}}'
                        for user_id in article['usuarios_destino']]
            # Añadir la lista formateada como cadena al campo 'cliente_destino'
            article['cliente_destino'] = json.loads(f'[{",".join(clientes)}]')
        # Eliminar la clave 'usuarios_destino' ya que no es necesaria en el archivo final
        del article['usuarios_destino']

    # Si el archivo de log mensual ya existe, cargar su contenido
    if os.path.exists(log_filepath):
        with open(log_filepath, 'r', encoding='utf-8') as log_file:
            noticias_archivadas = json.load(log_file)
    else:
        noticias_archivadas = []

    # Agregar las noticias filtradas al log mensual
    noticias_archivadas.extend(noticias_filtradas)

    # Guardar el log actualizado con indentación
    with open(log_filepath, 'w', encoding='utf-8') as log_file:
        json.dump(noticias_archivadas, log_file, ensure_ascii=False, indent=4)

    print(f"Noticias archivadas correctamente en {log_filepath}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python archivar_noticias.py <archivo_noticias_filtradas>")
        sys.exit(1)

    noticias_filtradas_file = sys.argv[1]
    archivar_noticias(noticias_filtradas_file)

