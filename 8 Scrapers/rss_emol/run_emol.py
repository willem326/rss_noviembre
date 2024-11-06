import subprocess
import os

# Obtener la ruta actual del script (run_scripts.py)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Si los archivos están en el mismo directorio, podemos usar los nombres directamente
rss_emol_path = os.path.join(current_directory, 'rss_emol.py')
emol_duplicados_path = os.path.join(current_directory, 'emol_duplicados.py')

# Ejecutar el primer script
subprocess.run(['python', rss_emol_path])

# Ejecutar el segundo script
subprocess.run(['python', emol_duplicados_path])
