# Librerias
import os
import sys
import pendulum
from datetime import timedelta
from pathlib import Path

# detecta la carpeta del archivo
DIRECTORIO_DAG = os.path.dirname(os.path.abspath(__file__))

# Le dice a Python que también busque scripts dentro de esta subcarpeta
if DIRECTORIO_DAG not in sys.path:
    sys.path.append(DIRECTORIO_DAG)

# Importa la clase DAG y operadores
from airflow.models import DAG
from airflow.operators.python import PythonOperator

# Importas tus módulos ETL y tu módulo de notificaciones
from extraccion.extraer import extraer
from transformacion.transformar import transformar
from carga.cargar import cargar
from notificacion.enviar_mails import alerta_fallo_etl, alerta_exito_etl

# Configuración de rutas absolutas
CARPETA_DATA = Path("/opt/airflow/data/agro_justo_mendoza_archivos")

# Configuracion del DAG
default_args = {
    "owner": "Nicolas",
    "start_date": pendulum.datetime(2024, 1, 1, tz="America/Argentina/Mendoza"), 
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,              
    "on_failure_callback": alerta_fallo_etl # 🟢 Airflow la llama automáticamente aquí si hay fallo
}

# Definimos el DAG
with DAG(
    dag_id="Agro_Justo_Mendoza",
    default_args=default_args,
    description="Pipeline de datos con Airflow para precios mayoristas y minoristas",
    schedule="30 12 * * 3", 
    catchup=False
) as dag:

    # Tarea 1: Extracción
    ejecutar_extraccion = PythonOperator(
        task_id="extraer",
        python_callable=extraer, 
        op_kwargs={"ruta_carpeta": CARPETA_DATA}, 
    )

    # Tarea 2: Transformación
    ejecutar_transformacion = PythonOperator(
        task_id="transformar",
        python_callable=transformar,
        op_kwargs={"ruta_carpeta": CARPETA_DATA}, 
    )

    # Tarea 3: Carga
    ejecutar_carga = PythonOperator(
        task_id="cargar",
        python_callable=cargar,
        op_kwargs={"ruta_carpeta": CARPETA_DATA}, 
    )

    # 🟢 Tarea 4: Enviar correo de Éxito
    ejecutar_notificacion_exito = PythonOperator(
        task_id="notificar_exito",
        python_callable=alerta_exito_etl,
        # En Airflow moderno, **context se pasa automáticamente
    )

    # Flujo de trabajo
    ejecutar_extraccion >> ejecutar_transformacion >> ejecutar_carga >> ejecutar_notificacion_exito