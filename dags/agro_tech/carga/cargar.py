import pandas as pd
import os
from sqlalchemy import text
from airflow.providers.postgres.hooks.postgres import PostgresHook
from agro_tech.registros.registro import proceso_log

# Función auxiliar para hacer UPSERT (Insertar nuevos o Actualizar existentes)
def upsert_postgresql(engine, df, table_name, pk_column):
    # 1. Subir los datos a una tabla temporal en PostgreSQL
    temp_table = f"{table_name}_temp"
    df.to_sql(temp_table, engine, if_exists="replace", index=False)

    # 2. Armar dinámicamente la consulta de actualización (excluyendo la clave primaria)
    columnas = list(df.columns)
    columnas_update = [f"{col} = EXCLUDED.{col}" for col in columnas if col != pk_column]
    update_str = ", ".join(columnas_update)

    # 3. Ejecutar sentencia INSERT ... ON CONFLICT
    query = f"""
        INSERT INTO {table_name} ({', '.join(columnas)})
        SELECT * FROM {temp_table}
        ON CONFLICT ({pk_column})
        DO UPDATE SET {update_str};
    """
    
    # Ejecutamos la consulta y luego borramos la tabla temporal
    with engine.begin() as conn:
        conn.execute(text(query))
        conn.execute(text(f"DROP TABLE {temp_table};"))

def cargar(ruta_carpeta):
    proceso_log("INICIO: Arranca la fase de carga de datos en PostgreSQL.")
    
    try:
        # Rutas de tablas
        ruta_productos = ruta_carpeta / "tabla_productos.xlsx"
        ruta_cotizaciones = ruta_carpeta / "tabla_cotizaciones.xlsx"
        ruta_sucursales = ruta_carpeta / "tabla_sucursales.xlsx"
        ruta_monitoreo_precios = ruta_carpeta / "fact_monitoreo_precios.xlsx"

        # Cargar tablas
        tabla_productos = pd.read_excel(ruta_productos)
        tabla_sucursales = pd.read_excel(ruta_sucursales)
        tabla_cotizaciones = pd.read_excel(ruta_cotizaciones)
        tabla_monitoreo = pd.read_excel(ruta_monitoreo_precios)
        
        proceso_log("INFO: Archivos Excel finales listos para ser cargados en la BD.")

        # Convertir nombres de columnas a minúsculas por seguridad en Postgres
        tabla_productos.columns = [c.lower() for c in tabla_productos.columns]
        tabla_sucursales.columns = [c.lower() for c in tabla_sucursales.columns]
        tabla_cotizaciones.columns = [c.lower() for c in tabla_cotizaciones.columns]
        tabla_monitoreo.columns = [c.lower() for c in tabla_monitoreo.columns]

        # Credenciales de la base de datos
        POSTGRES_CONN_ID = "agro_justo_mendoza"

        # Carga en la base de datos
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        engine = pg_hook.get_sqlalchemy_engine()
        print("Conexión exitosa a la BD")
        proceso_log("INFO: Conexión exitosa a la base de datos PostgreSQL.")

        # ==========================================
        # 1. CARGA DE DIMENSIONES (Evita duplicados)
        # ==========================================
        print("Cargando dimensión: sucursales...")
        upsert_postgresql(engine, tabla_sucursales, "sucursales", "id_sucursal")

        print("Cargando dimensión: productos...")
        upsert_postgresql(engine, tabla_productos, "productos", "id_producto")
        
        proceso_log("INFO: Dimensiones (sucursales, productos) actualizadas correctamente vía UPSERT.")

        # ==========================================
        # 2. CARGA DE HECHOS (Conserva el histórico)
        # ==========================================
        print("Cargando hechos: cotizaciones_divisas...")
        tabla_cotizaciones.to_sql("cotizaciones_divisas", con=engine, if_exists="append", index=False)

        print("Cargando hechos: monitoreo_precios...")
        tabla_monitoreo.to_sql("monitoreo_precios", con=engine, if_exists="append", index=False)
        
        proceso_log("INFO: Tablas de hechos (cotizaciones, monitoreo) agregadas correctamente vía APPEND.")
        
        print("Datos cargados correctamente en la Base de Datos")
        proceso_log("FIN: Carga de datos exitosa. Pipeline ETL finalizado.\n")
    
    except Exception as ex:
        print("No se pudieron cargar los datos")
        print(ex)
        proceso_log(f"ERROR CRÍTICO: Fallo durante la carga en la Base de Datos. Detalle: {ex}")
        raise # fuerza el fallo del DAG en caso de error

    # datos extra del RETURN
    total_productos = len(tabla_monitoreo)
    total_sucursales = len(tabla_sucursales)
    cotizacion_dolar = float(tabla_cotizaciones["valor"].iloc[0])

    return {
        "productos": total_productos,
        "sucursales": total_sucursales,
        "dolar_blue": cotizacion_dolar
    }