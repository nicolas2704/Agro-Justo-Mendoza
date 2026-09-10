from datetime import datetime
from pathlib import Path
import pytz # Importación necesaria para el manejo de zonas horarias

# Registro de procesos
def proceso_log(mensaje):
    # 1. Obtener la ruta absoluta del directorio donde está ESTE script (registro.py)
    directorio_actual = Path(__file__).resolve().parent
    
    # 2. Definir la ruta de la carpeta "registros" junto a este script
    ruta_carpeta_registros = directorio_actual / "archivos_logs"
    
    # 3. Crear la carpeta dinámicamente si no existe (evita errores en Docker)
    ruta_carpeta_registros.mkdir(parents=True, exist_ok=True)
    
    # 4. Definir la ruta completa del archivo de log
    archivo_registro = ruta_carpeta_registros / "agro_justo_etl_log.txt"
    
    # 5. Configurar la zona horaria local
    zona_horaria = pytz.timezone('America/Argentina/Mendoza')
    
    # 6. Formato y escritura (aplicando la zona horaria al datetime)
    formato_tiempo = "%Y-%m-%d %H:%M:%S" 
    fecha_actual = datetime.now(zona_horaria) # ¡Aquí le pasamos la zona horaria!
    marca_de_tiempo = fecha_actual.strftime(formato_tiempo)
    
    # Abre o crea el archivo y añade el texto
    with open(archivo_registro, "a", encoding="utf-8") as registro: 
        registro.write(f"{marca_de_tiempo} // {mensaje}\n")