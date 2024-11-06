import subprocess
import os
from datetime import datetime
import time

# Directorio base donde están las carpetas con los scrapers
base_dir = './8 scrapers/'
# Directorio donde se guardarán los logs
log_dir = './log/'

# Lista de nombres de los scrapers, que coinciden con los nombres de las carpetas
scrapers = [
    "rss_biobio",
    "run_emol",  # Esta entrada ejecutará un flujo especial
    "rss_mostrador",
    "rss_chv",
    "rss_lacuarta",
    "rss_cnn",
    "rss_ciudadano",
    "rss_t13"
]

# Crear el directorio de logs si no existe
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def escribir_log(mensaje):
    """Escribe el mensaje en el archivo de log con timestamp, en orden inverso (último mensaje primero)."""
    log_file = os.path.join(log_dir, 'scrapers_especiales.log')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {mensaje}\n"
    
    # Leer contenido existente del log si lo hay
    contenido = ""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            contenido = f.read()
    
    # Escribir el nuevo log al inicio, y luego el contenido anterior
    with open(log_file, 'w') as f:
        f.write(log_entry + contenido)

def formatear_tiempo(segundos):
    """Convierte los segundos a formato minutos:segundos (mm:ss)"""
    minutos = segundos // 60
    segundos = int(segundos % 60)
    return f"{minutos:02}:{segundos:02}"

def ejecutar_scraper(scraper):
    """Función para ejecutar un scraper individual."""
    scraper_path = os.path.join(base_dir, scraper, f"{scraper}.py")
    if os.path.exists(scraper_path):
        try:
            start_time = time.time()  # Tiempo de inicio
            escribir_log(f"Iniciando {scraper}.py desde {scraper_path}")
            print(f"Ejecutando {scraper}.py desde {scraper_path}...")
            
            result = subprocess.run(['python', scraper_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Intentar decodificar primero en UTF-8, luego en latin-1 si falla
            try:
                stdout_decoded = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                stdout_decoded = result.stdout.decode('latin-1')

            try:
                stderr_decoded = result.stderr.decode('utf-8')
            except UnicodeDecodeError:
                stderr_decoded = result.stderr.decode('latin-1')

            end_time = time.time()  # Tiempo de fin
            elapsed_time = end_time - start_time  # Tiempo transcurrido en segundos
            tiempo_formateado = formatear_tiempo(elapsed_time)
            
            escribir_log(f"{scraper}.py terminado con éxito en {tiempo_formateado}. Código de salida: {result.returncode}")
            escribir_log(f"Salida: {stdout_decoded}")
            if stderr_decoded:
                escribir_log(f"Errores: {stderr_decoded}")

        except subprocess.CalledProcessError as e:
            error_message = f"Error al ejecutar {scraper}.py: {e}. Código de salida: {e.returncode}"
            escribir_log(error_message)
            print(error_message)

    else:
        mensaje_error = f"El script {scraper}.py no se encontró en la ruta: {scraper_path}"
        escribir_log(mensaje_error)
        print(mensaje_error)

def ejecutar_scraper_emol():
    """Ejecución especial para Emol: Ejecuta rss_emol.py y luego emol_duplicados.py"""
    try:
        # Ejecutar rss_emol.py
        escribir_log(f"Iniciando rss_emol.py en el flujo Emol.")
        result = subprocess.run(['python', os.path.join(base_dir, 'rss_emol', 'rss_emol.py')], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        escribir_log(f"rss_emol.py terminado con éxito. Código de salida: {result.returncode}")
        escribir_log(f"Salida: {result.stdout.decode('utf-8', errors='ignore')}")

        # Ejecutar emol_duplicados.py después
        escribir_log(f"Iniciando emol_duplicados.py en el flujo Emol.")
        result = subprocess.run(['python', os.path.join(base_dir, 'rss_emol', 'emol_duplicados.py')], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        escribir_log(f"emol_duplicados.py terminado con éxito. Código de salida: {result.returncode}")
        escribir_log(f"Salida: {result.stdout.decode('utf-8', errors='ignore')}")

    except subprocess.CalledProcessError as e:
        error_message = f"Error en el proceso Emol: {e}. Código de salida: {e.returncode}"
        escribir_log(error_message)
        print(error_message)

def main():
    start_time_total = time.time()  # Tiempo de inicio total
    escribir_log("************************************************************")
    escribir_log("Inicio de ejecución de scrapers especiales.")
    
    for scraper in scrapers:
        if scraper == "run_emol":
            # Ejecución especial para el flujo de Emol
            ejecutar_scraper_emol()
        else:
            # Ejecución estándar para otros scrapers
            ejecutar_scraper(scraper)
    
    end_time_total = time.time()  # Tiempo de fin total
    elapsed_time_total = end_time_total - start_time_total  # Tiempo total transcurrido
    tiempo_total_formateado = formatear_tiempo(elapsed_time_total)
    
    escribir_log(f"Finalización de ejecución de scrapers especiales. Tiempo total: {tiempo_total_formateado}")
    escribir_log("************************************************************")
    print(f"Tiempo total de ejecución de todos los scrapers: {tiempo_total_formateado}")

if __name__ == "__main__":
    main()
