import pandas as pd
import google.generativeai as genai
import requests
import glob
import os
import time
import json
from datetime import datetime
from extraccion.extraer_precios_super import obtener_precio_web
from agro_tech.registros.registro import proceso_log

def extraer(ruta_carpeta):
    proceso_log("INICIO: Comenzando proceso de extracción de datos (PDF, Divisas y Supermercados).")
    # API para utilizar GEMINI
    API_KEY = "Escribir su API_KEY"

    # identificando con Google para que permita el acceso
    genai.configure(api_key=API_KEY)

    # RUTAS ENTRADAS ARCHIVOS
    # ruta del archivo PDF
    ruta_pdf = ruta_carpeta
    # ruta archivo EXCEL MAESTRO
    archivo_maestro = ruta_carpeta / "maestro_urls.xlsx"
    # archivo precios coto
    archivo_precios_coto = ruta_carpeta / "precios_coto.xlsx"

    # RUTAS SALIDA
    # ruta cotizaciones
    ruta_cotizaciones = ruta_carpeta / "tabla_cotizaciones.xlsx"
    # ruta precios feria
    ruta_df_productos = ruta_carpeta / "df_productos_feria.xlsx"
    # ruta del scrapeo de SUPERMERCADOS con precios
    ruta_super_precios = ruta_carpeta / "supermercados_precios.xlsx"


    # API USD
    dolar_arg= requests.get("Escribir API de Moneda")

    # identifica los archivos .PDF de la ruta y los guarda en una lista
    archivo_pdf = glob.glob(os.path.join(ruta_pdf, "*.pdf"))

    # archivo coto
    precios_coto = pd.read_excel(archivo_precios_coto)

    # EXTRAER DATOS
    # Cargar archivo excel
    dataframe_maestro=pd.read_excel(archivo_maestro)
    # Toma el PDF local, lo sube a Gemini y extrae datos específicos.
    
    # Verificacion de que exista el archivo
    plantilla_nula = {
        "metadata": {
            "fecha_detectada": datetime.now().strftime("%Y-%m-%d")
        },
        "hortalizas": [
            {"producto_idr": "Batata", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Cebolla Valenciana", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Lechuga Repollada", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Papa Spunta", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Pepino", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Perejil", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Atado", "precio_mayorista": None},
            {"producto_idr": "Pimiento Rojo", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Pimiento Verde", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Tomate Redondo", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Tomate Perita", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Zanahoria", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Zapallo Anquito", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Zapallito Redondo", "variedad_encontrada": "N/A", "categoria": "Hortaliza", "unidad": "Kilogramo", "precio_mayorista": None}
        ],
        "frutas": [
            {"producto_idr": "Banana", "variedad_encontrada": "N/A", "categoria": "Fruta", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Limón", "variedad_encontrada": "N/A", "categoria": "Fruta", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Manzana", "variedad_encontrada": "N/A", "categoria": "Fruta", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Naranja", "variedad_encontrada": "N/A", "categoria": "Fruta", "unidad": "Kilogramo", "precio_mayorista": None},
            {"producto_idr": "Palta", "variedad_encontrada": "N/A", "categoria": "Fruta", "unidad": "Kilogramo", "precio_mayorista": None}
        ]
    }

    # Verificacion de que exista el archivo
    if not archivo_pdf:
        mensaje_warn = f"ADVERTENCIA: No se encontró PDF en {ruta_pdf}. Se aplicó plantilla nula."
        print(f"Advertencia: No se encuentra el archivo PDF en: {ruta_pdf}.")
        print("Se cargarán los precios del PDF como nulos (vacíos) para continuar...")
        proceso_log(mensaje_warn)
        datos_productos = plantilla_nula
    else:
        # identifica el archivo .PDF
        ruta_pdf_detectado=archivo_pdf[0]
        proceso_log(f"PDF detectado: {ruta_pdf_detectado}. Enviando a Gemini AI...")
        print(f"Iniciando proceso para: {ruta_pdf_detectado}")   

        # Sube el archivo a la nube de GEMINI
        print("Subiendo archivo a Google AI..")
        archivo_subido = genai.upload_file(ruta_pdf_detectado, mime_type="application/pdf")
        
        # el proceso demora y espera 2 segundos para volver a preguntar
        while archivo_subido.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            archivo_subido = genai.get_file(archivo_subido.name)
        print(" ¡Listo!")

        # Se utiliza el modelo PRO de GEMINI para la extraccion
        model = genai.GenerativeModel("models/gemini-2.5-flash")

        prompt = """Actúa como un Experto en Ingeniería de Datos y Extracción OCR.
        Analiza el texto completo del PDF adjunto y genera un archivo JSON puro con los datos de las tablas "HORTALIZAS" y "FRUTAS".

        ---
        1. REGLAS DE DETECCIÓN DE COLUMNA DE PRECIOS (DINÁMICA):
        - El PDF contiene matrices de datos. NO busques una fecha fija.
        - **Lógica de Localización:** Identifica la columna de precios vigente buscando aquella que:
            a) Contiene el símbolo "$" y valores numéricos.
            b) Está ubicada inmediatamente a la IZQUIERDA de la columna "Variación" o "Semana anterior".
        - **Fecha del Reporte:** Extrae la fecha que aparece en ese encabezado y normalízala a "YYYY-MM-DD" (asume el año actual si no figura).

        ---
        2. EXTRACCIÓN DE PRODUCTOS:
        Busca las siguientes filas en sus respectivas tablas. Extrae la "Unidad" y el "Precio Vigente" detectado. Usa coincidencia aproximada si el nombre varía levemente.

        A. SECCIÓN HORTALIZAS:
        - "Batata": (Buscar variedad "Arapey").
        - "Cebolla Valenciana": (Buscar "Cebolla" -> "Valenciana").
        - "Lechuga Repollada": (Buscar "Lechuga" -> variedad "Repollada").
        - "Papa Spunta (Lavada)": (Buscar "Papa" -> variedad "Lavada" o "Spunta Lavada").
        - "Pepino": (Buscar "Pepino" -> variedad "Verde", "Común" o genérico).
        - "Perejil": (Cualquier variedad).
        - "Pimiento Cuatro Cascos Rojo": (Buscar "Pimiento" -> variedad "Rojo" o "Cuatro Cascos Rojo").
        - "Pimiento Cuatro Cascos Verde": (Buscar "Pimiento" -> variedad "Verde" o "Cuatro Cascos Verde").
        - "Tomate Redondo": (Buscar "Tomate" -> "Redondo" o "Perita Redondo").
        - "Tomate Perita": (Buscar "Tomate" -> variedad "Perita").
        - "Zanahoria": (Buscar Calidad "Primera" o variedad "Flakkee").
        - "Zapallo Anquito": (Buscar "Zapallo" -> variedad "Anquito").
        - "Zapallito Redondo": (Buscar "Zapallito" -> "Redondo").

        B. SECCIÓN FRUTAS:
        - "Banana": (Buscar variedad "Cavendish" o procedencia "Ecuador").
        - "Limón": (Buscar variedad "Eureka" o similar).
        - "Manzana Red Delicious": (Buscar variedad "Red Delicious". Si no existe, usa "Granny Smith" como fallback).
        - "Naranja": (Buscar variedad "Valencia" o "Jugo").
        - "Palta Elegido": (Buscar "Palta" -> variedad "Hass" o Calidad "Elegido").

        ---
        3. REGLAS DE LIMPIEZA DE DATOS (CRÍTICO PARA SQL):
        - **Precio:** Debe ser un número FLOTANTE (Float) válido.
            * Eliminar el símbolo "$".
            * Eliminar el punto de miles (".").
            * Reemplazar la coma decimal (",") por un punto (".").
            * Ejemplo: Transformar "$ 1.409,09" -> 1409.09
        - **Unidad:** Texto limpio (ej: "Kilogramo", "Atado", "Cajón").
        - **Categoria:** Debe ser ("Hortaliza" o "Fruta") segun la tabla donde se ubica el producto.

        ---
        4. FORMATO DE SALIDA (JSON):
        Devuelve SOLAMENTE el siguiente objeto JSON, sin bloques de código markdown, sin texto introductorio ni final.

        {
        "metadata": {
            "fecha_detectada": "YYYY-MM-DD"
        },
        "hortalizas": [
            {
            "producto_idr": "Batata",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Cebolla Valenciana",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Lechuga Repollada",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Papa Spunta",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Pepino",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Perejil",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Pimiento Rojo",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Pimiento Verde",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Tomate Redondo",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Tomate Perita",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Zanahoria",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Zapallo Anquito",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Zapallito Redondo",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            }
        ],
        "frutas": [
            {
            "producto_idr": "Banana",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Limón",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Manzana",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Naranja",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            },
            {
            "producto_idr": "Palta",
            "variedad_encontrada": "Texto detectado",
            "categoria" : "Texto detectado",
            "unidad": "Texto detectado",
            "precio_mayorista": 0.00
            }
        ]
        }
        """
        # Genera el archivo de PDF a JSON
        print("Consultando a Gemini...")
        response = model.generate_content([archivo_subido, prompt])
        
        # LIMPIEZA en caso de haber anomalias
        # Quitamos las comillas de código que a veces pone la IA (```json ... ```)
        try:
            json_string = response.text.replace("```json", "").replace("```", "").strip()
            datos_productos = json.loads(json_string)
            proceso_log("EXITO: Extracción OCR de Gemini completada correctamente.")
        except Exception as e:
            mensaje_err = "ERROR/BLOQUEO en Gemini AI. Se aplicó plantilla nula."
            # Si entra aquí, es porque la IA bloqueó la respuesta o devolvió texto inválido
            print("ALERTA: Hubo un problema con la respuesta de la IA (bloqueo o mal formato).")
            proceso_log(mensaje_err)
            if hasattr(response, 'prompt_feedback'):
                print(f"Razón del bloqueo: {response.prompt_feedback}")
            else:
                print(f"Error técnico: {e}")
                
            # Opción B: Asignamos la plantilla con nulls para que el programa no colapse
            print("Se cargarán los precios como nulos debido al error en la IA.")
            datos_productos = plantilla_nula

    indice=1
    # transformar los datos de las HORTALIZAS del JSON en un DATAFRAME
    filas_dataframe_hortalizas = []
    fecha = datos_productos["metadata"]["fecha_detectada"]
    for item in datos_productos["hortalizas"]:
        fila_hortaliza = {
            "indice":indice,
            "fecha": fecha,
            "nombre_producto": item["producto_idr"], # Usamos la variable directa
            "categoria": item["categoria"],
            "unidad":item["unidad"], # usamos la variable directa
            "precio_pesos": item["precio_mayorista"], # Usamos la variable directa
        }
        indice+=1
        filas_dataframe_hortalizas.append(fila_hortaliza)

    # TABLA PRODUCTOS
    # Convertimos a DataFrame
    dataframe_hortalizas = pd.DataFrame(filas_dataframe_hortalizas)

    # transformar los datos de las FRUTAS del JSON en un DATAFRAME
    filas_dataframe_frutas = []
    fecha = datos_productos["metadata"]["fecha_detectada"]
    for item in datos_productos["frutas"]:
        fila_fruta = {
            "indice":indice,
            "fecha": fecha,
            "nombre_producto": item["producto_idr"], # Usamos la variable directa
            "categoria": item["categoria"],
            "unidad":item["unidad"], # usamos la variable directa
            "precio_pesos": item["precio_mayorista"], # Usamos la variable directa
        }
        indice+=1
        filas_dataframe_frutas.append(fila_fruta)

    # Convertimos a DataFrame
    dataframe_frutas = pd.DataFrame(filas_dataframe_frutas)

    # unir dataframes
    dataframe=pd.concat([dataframe_hortalizas, dataframe_frutas], ignore_index=True) # une el dataframe vacio con el anterior no superponiendo sus indices
    # usar el EXCEL MAESTRO
    # utilizamos solos las columnas necesarias
    productos_imagen=dataframe_maestro[["nombre_producto","url_imagen"]]
    # eliminados filas con nombres duplicados
    dataframe_limpio_imagen=productos_imagen.drop_duplicates(subset="nombre_producto", keep="first")
    # unir la columna de imagenes al dataframe de los productos
    dataframe_productos= dataframe.merge(dataframe_limpio_imagen, on="nombre_producto", how="left")
    print(dataframe_productos)

    # TABLA COTIZACIONES DE DIVISAS
    try:
        fecha_hoy = datetime.now()
        id_fecha_fk = int(fecha_hoy.strftime('%Y%m%d'))
        dolar_arg= requests.get("Escribir API de Moneda")
        monedas_argentinas = dolar_arg.json()
        for item in monedas_argentinas:
            if item["casa"] =="blue":
                venta_dolar_blue = item["venta"]
                tipo_divisa = item["moneda"]
                break
        proceso_log(f"EXITO: Cotización Dólar Blue obtenida (${venta_dolar_blue}).")
    except Exception as e:
        print("Aviso: No se pudo conectar a la API del dólar.")
        proceso_log("ADVERTENCIA: Falló la API del Dólar. Revisa la conexión.")
    
    dic_cotizaciones_divisas = {
        "id_fecha" : [id_fecha_fk],
        "tipo_divisa": [tipo_divisa],
        "valor": [venta_dolar_blue]
    }
    dataframe_cotizaciones=pd.DataFrame(dic_cotizaciones_divisas)

    # Extraer datos del los Supermercados
    # 3. EJECUCIÓN DEL PROCESO
    datos_recolectados = []

    print("\n--- INICIANDO ESCANEO DE PRECIOS ---")
    proceso_log(f"SCRAPING: Iniciando escaneo de precios en supermercados para {len(dataframe_maestro)} productos...")

    # Iteramos usando las columnas exactas de tu archivo
    for index, fila in dataframe_maestro.iterrows():
        # Extraemos datos de TU archivo (nombres de columnas basados en tu CSV)
        id_maestro = fila['id_producto_idr'] # Conservamos el ID correcto (1 al 18)
        nombre_prod = fila['nombre_producto']
        supermercado = fila['supermercado'] 
        url_target = fila['url_producto_target'] 
        categoria = fila['categoria']
        
        print(f"[{index+1}/{len(dataframe_maestro)}] Buscando {nombre_prod} en {supermercado}...")
        
        # Llamamos a la funcion robot con las filas de las url y supermercado
        # Obtenemos los IDs del Excel (si la celda está vacía, Pandas devuelve NaN, lo cual está manejado en la función)
        # Asegúrate de nombrar estas columnas así en tu Excel
        id_sku = fila.get('sku_id_supermercado', None) 
        id_prod = fila.get('product_id_supermercado', None)

        # Llamamos a la funcion robot pasando los parámetros extra
        # Llamamos a la nueva función que solo necesita el nombre del súper y el SKU
        precio = obtener_precio_web(supermercado,precios_coto, dataframe_url=url_target, sku_id=id_sku, id_producto=id_maestro)
        
        # Guardamos resultado
        datos_recolectados.append({
            "fecha_actual": datetime.now().strftime("%Y-%m-%d"),
            "id_producto": id_maestro,
            "categoria": categoria,
            "producto": nombre_prod,
            "supermercado": supermercado,
            "precio_encontrado": precio, # Puede ser un número o None (vacío)
            "url_chequeada": url_target
        })

    proceso_log("SCRAPING: Búsqueda de precios en supermercados finalizada.")
    # 4. GENERAR DATAFRAME FINAL
    df_precios_super = pd.DataFrame(datos_recolectados)
    # Todo en una sola línea usando *=
    df_precios_super.loc[(df_precios_super["id_producto"] == 18) & (df_precios_super["supermercado"] == "Vea"), "precio_encontrado"] *= 5
    df_precios_super.loc[(df_precios_super["id_producto"] == 18) & (df_precios_super["supermercado"] == "Jumbo"), "precio_encontrado"] *= 5
    df_precios_super.loc[(df_precios_super["id_producto"] == 18) & (df_precios_super["supermercado"] == "Carrefour"), "precio_encontrado"] *= 5

    # 5. PEQUEÑA LIMPIEZA FINAL (Eliminar filas donde no se encontró precio si quieres)
    # df_resultados = df_resultados.dropna(subset=['precio_encontrado'])

    print("\n--- PROCESO TERMINADO ---")
    # print(df_precios_super)

    # EXPORTAR DATAFRAMES
    # Exportar dataframe precios feria
    dataframe_productos.to_excel(ruta_df_productos, index=False)

    # Exportar dataframe cotizaciones
    dataframe_cotizaciones.to_excel(ruta_cotizaciones, index=False)

    # Exportar dataframe supermercados
    df_precios_super.to_excel(ruta_super_precios, index=False)

    proceso_log("FIN: Archivos Excel exportados con éxito. Etapa de Extracción completada.\n")
    