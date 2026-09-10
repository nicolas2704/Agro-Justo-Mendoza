import pandas as pd
from datetime import datetime
import pytz

from agro_tech.registros.registro import proceso_log
from agro_tech.notificacion.enviar_mails import alerta_brecha_extrema

def transformar(ruta_carpeta):
    proceso_log("INICIO: Arranca la fase de transformación de datos.")
    # Definimos la zona horaria
    zona_horaria = pytz.timezone('America/Argentina/Mendoza')
    try:
        # rutas entrada de dataframes
        archivo_productos_feria = ruta_carpeta / "df_productos_feria.xlsx"
        archivo_super = ruta_carpeta / "supermercados.xlsx"
        archivo_super_precios = ruta_carpeta / "supermercados_precios.xlsx"

        # ruta salida de tablas
        ruta_productos = ruta_carpeta / "tabla_productos.xlsx"
        ruta_cotizaciones = ruta_carpeta / "tabla_cotizaciones.xlsx"
        ruta_sucursales = ruta_carpeta / "tabla_sucursales.xlsx"
        ruta_monitoreo_precios = ruta_carpeta / "fact_monitoreo_precios.xlsx"

        # CARGAR ARCHIVOS
        dataframe_productos = pd.read_excel(archivo_productos_feria)
        dataframe_cotizaciones = pd.read_excel(ruta_cotizaciones)
        dataframe_super_precios = pd.read_excel(archivo_super_precios)
        dataframe_sucursales = pd.read_excel(archivo_super)
        
        proceso_log("INFO: Archivos Excel de extracción cargados correctamente.")
        print("\n--- INICIANDO TRANSFORMACIÓN ---")

        # TABLA SUCURSALES
        tabla_sucursales = dataframe_sucursales

        # TABLA PRODUCTOS
        # eliminar columnas innecesarias
        tabla_productos = dataframe_productos.drop(['fecha','precio_pesos'], axis=1)

        # TABLA COTIZACIONES
        # pasar valores de dolar a float64
        dataframe_cotizaciones["valor"] = dataframe_cotizaciones["valor"].astype("float64")
        tabla_cotizaciones = dataframe_cotizaciones
        
        proceso_log("INFO: Dimensiones (Sucursales, Productos) y Cotizaciones procesadas.")

        # CREACION TABLA MONITOREO_PRECIOS
        print("\n--- CREANDO TABLA DE HECHOS: FACT_MONITOREO_PRECIOS ---")
        proceso_log("INFO: Construyendo tabla de hechos 'fact_monitoreo_precios'...")

        hora_mendoza = datetime.now(zona_horaria).replace(tzinfo=None)
        
        # ==============================================================
        # 1. PROCESAR SUCURSALES (SUPERMERCADOS)
        # ==============================================================
        df_hechos_super = dataframe_super_precios.copy()

        # GENERAR id_fecha_precio (Smart Key YYYYMMDD)
        df_hechos_super['fecha_actual'] = pd.to_datetime(df_hechos_super['fecha_actual'])
        df_hechos_super['id_fecha_precio'] = df_hechos_super['fecha_actual'].dt.strftime('%Y%m%d').astype(int)

        # GENERAR fecha_ejecucion_dag
        df_hechos_super['fecha_ejecucion_dag'] = hora_mendoza

        # MAPEAMOS EL id_sucursal (El enlace con dim_sucursales)
        mapa_sucursales = dict(zip(tabla_sucursales['supermercado'], tabla_sucursales['indice']))
        df_hechos_super['id_sucursal'] = df_hechos_super['supermercado'].map(mapa_sucursales)

        # RENOMBRAMOS LA MÉTRICA 
        df_hechos_super = df_hechos_super.rename(columns={'precio_encontrado': 'precio_publicado'})

        # FILTRAMOS Y ORDENAMOS LAS COLUMNAS (La estructura final)
        columnas_fact_table = [
            'id_fecha_precio',
            'id_producto',
            'id_sucursal',
            'precio_publicado',
            'fecha_ejecucion_dag'
        ]
        
        df_hechos_super = df_hechos_super[columnas_fact_table]

        # ==============================================================
        # 2. PROCESAR FERIA (MERCADO COOPERATIVO)
        # ==============================================================
        df_hechos_feria = dataframe_productos.copy()
        
        # GENERAR id_fecha_precio (Viene de la columna 'fecha' detectada por la IA)
        df_hechos_feria['fecha_actual'] = pd.to_datetime(df_hechos_feria['fecha'])
        df_hechos_feria['id_fecha_precio'] = df_hechos_feria['fecha_actual'].dt.strftime('%Y%m%d').astype(int)
        
        # GENERAR fecha_ejecucion_dag
        # PONER ESTO
        df_hechos_feria['fecha_ejecucion_dag'] = hora_mendoza
        
        # MAPEO DE CLAVES FORÁNEAS
        df_hechos_feria['id_producto'] = df_hechos_feria['indice']
        
        # Asignamos el ID fijo de la sucursal 6 para el Mercado Cooperativo
        df_hechos_feria['id_sucursal'] = 6
        
        # RENOMBRAMOS LA MÉTRICA
        df_hechos_feria = df_hechos_feria.rename(columns={'precio_pesos': 'precio_publicado'})
        
        # FILTRAMOS Y ORDENAMOS LAS COLUMNAS
        df_hechos_feria = df_hechos_feria[columnas_fact_table]

        # ==============================================================
        # 3. UNIÓN DE LOS DATOS Y LIMPIEZA FINAL
        # ==============================================================
        # Apilamos los dos dataframes
        tabla_monitoreo_precios = pd.concat([df_hechos_super, df_hechos_feria], ignore_index=True)

        proceso_log("INFO: Datos de supermercados y feria unidos con éxito en la tabla de hechos.")
        print("¡Transformación exitosa! Muestra del resultado final (Supermercados + Feria):")
        print(tabla_monitoreo_precios.head())
        print(tabla_monitoreo_precios.tail())

        # ==============================================================
        # 🟢 4. CÁLCULO DE BRECHA Y ALERTA DE RENTABILIDAD EXTREMA
        # ==============================================================
        proceso_log("INFO: Analizando brechas de precios para alertas...")
        
        # Separar precios para comparar (Solo nos importan los precios de hoy)
        precios_feria = df_hechos_feria[['id_producto', 'precio_publicado']].rename(columns={'precio_publicado': 'precio_feria'})
        precios_super = df_hechos_super[['id_producto', 'id_sucursal', 'precio_publicado']].rename(columns={'precio_publicado': 'precio_super'})

        # Unir supermercados con la feria por producto
        df_brecha = pd.merge(precios_super, precios_feria, on='id_producto', how='inner')

        # Fórmula matemática de la brecha %
        df_brecha['brecha_pct'] = ((df_brecha['precio_super'] - df_brecha['precio_feria']) / df_brecha['precio_feria']) * 100

        # Filtrar los que superan el 300%
        UMBRAL = 300
        df_alertas = df_brecha[df_brecha['brecha_pct'] >= UMBRAL].copy()

        # Si encontramos alertas, armamos el correo
        if not df_alertas.empty:
            # Traer el nombre del producto y la URL de la imagen de tabla_productos
            df_alertas = pd.merge(df_alertas, dataframe_productos[['indice', 'nombre_producto', 'url_imagen']], left_on='id_producto', right_on='indice', how='left')
            # Traer el nombre del supermercado
            df_alertas = pd.merge(df_alertas, dataframe_sucursales[['indice', 'supermercado']], left_on='id_sucursal', right_on='indice', how='left')
            
            # Construir la lista para el mail
            lista_alertas = []
            for _, row in df_alertas.iterrows():
                lista_alertas.append({
                    "producto": str(row['nombre_producto']).title(),
                    "supermercado": str(row['supermercado']),
                    "brecha": round(row['brecha_pct'], 1),
                    "precio_super": round(row['precio_super'], 2),
                    "precio_feria": round(row['precio_feria'], 2),
                    "url_imagen": str(row['url_imagen'])
                })
            
            try:
                alerta_brecha_extrema(lista_alertas)
                proceso_log(f"ALERTA ENVIADA: Se detectaron {len(lista_alertas)} productos con brecha extrema.")
            except Exception as e:
                proceso_log(f"ERROR: Falló el envío del correo de alertas. Detalle: {e}")
        else:
            proceso_log("INFO: Ningún producto superó el umbral de alerta de brecha.")

        # ==============================================================
        # EXPORTACION DE ARCHIVOS PARA LA CARGA
        # ==============================================================
        proceso_log("INFO: Generando archivos Excel finales para la carga en Base de Datos...")
        
        tabla_sucursales = tabla_sucursales.rename(columns={"indice": "id_sucursal"})
        tabla_sucursales = tabla_sucursales.rename(columns={"supermercado": "nombre_cadena"})
        # TABLA SUCURSALES
        tabla_sucursales.to_excel(ruta_sucursales, index=False)
        
        # TABLA PRODUCTOS
        tabla_productos = tabla_productos.rename(columns={"indice" : "id_producto"})
        tabla_productos = tabla_productos.rename(columns={"unidad": "unidad_medida"})
        tabla_productos.to_excel(ruta_productos, index=False)
        
        # TABLA COTIZACIONES
        tabla_cotizaciones.to_excel(ruta_cotizaciones, index=False)
        
        # TABLA MONITOREO PRECIOS
        tabla_monitoreo_precios.to_excel(ruta_monitoreo_precios, index=False)
        
        proceso_log("FIN: Transformación y exportación completadas exitosamente.\n")

    except Exception as e:
        proceso_log(f"ERROR CRÍTICO: Fallo durante la transformación de datos. Detalle: {e}")
        raise # Vuelve a lanzar el error para que Airflow marque la tarea como fallida