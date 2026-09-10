FROM apache/airflow:3.0.0-python3.10

USER root
# 1. Actualizamos el gestor de paquetes e instalamos Java (JDK)
RUN apt-get update && \
    apt-get install -y default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Volvemos al usuario de Airflow para instalar los paquetes de Python
USER airflow

# Copiamos el archivo de requerimientos al contenedor
COPY requirements.txt /

# Instalamos las librerías usando pip
RUN pip install --no-cache-dir -r /requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.0.0/constraints-3.10.txt"
