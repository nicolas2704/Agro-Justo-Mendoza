import os
from pathlib import Path
import pendulum  # 🟢 IMPORTANTE: Importamos pendulum para manejar zonas horarias
from airflow.utils.email import send_email

# Como este script está en la carpeta 'notificacion', 
# usamos .parent.parent para "subir" al directorio principal del proyecto.
DIRECTORIO_BASE = Path(__file__).resolve().parent.parent

# Lista de correos a los que quieres notificar
lista_destinatarios = [
    "Escribir los correos que desea notificar"
]

# ==============================================================
# 🔴 FUNCIÓN DE ALERTA: ERROR (La que ya tenías)
# ==============================================================
def alerta_fallo_etl(context):
    task_instance = context.get('task_instance')
    task_id = task_instance.task_id
    excepcion = context.get('exception')
    
    # CORRECCIÓN DE ZONA HORARIA
    logical_date = context.get('logical_date')
    if logical_date:
        # Convertimos la fecha UTC de Airflow a la hora local de Mendoza
        fecha_local = pendulum.instance(logical_date).in_timezone('America/Argentina/Mendoza')
        fecha_ejecucion = fecha_local.strftime("%Y-%m-%d %H:%M:%S")
    else:
        fecha_ejecucion = "Desconocida"
    
    ruta_log = DIRECTORIO_BASE / "agro_tech" / "registros" / "archivos_logs" / "agro_justo_etl_log.txt"
    url_imagen_github = "https://github.com/nicolas2704/Agro-Justo-Mendoza/blob/main/imagenes/imagen_error_pipeline.png?raw=true"
    
    ultimas_lineas = f"No se pudo acceder al archivo de registro local en la ruta:\n{ruta_log}"
    
    try:
        if ruta_log.exists():
            with open(ruta_log, 'r', encoding='utf-8') as archivo:
                lineas = archivo.readlines()
                ultimas_lineas = "".join(lineas[-15:])
    except Exception as e:
        ultimas_lineas = f"Error al intentar leer el archivo de log local: {str(e)}"

    imagen_html = f'''
    <div style="text-align: center; background-color: #f9f9f9; padding: 15px; border-bottom: 1px solid #eeeeee;">
        <img src="{url_imagen_github}" alt="Diagrama del Pipeline" style="max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    </div>
    '''

    asunto = f"🚨 ALERTA AIRFLOW: Fallo en Agro Justo Mendoza - Tarea: {task_id}"
    cuerpo_correo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }}
            .container {{ max-width: 650px; margin: auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border: 1px solid #e0e0e0; }}
            .header {{ background-color: #d9534f; color: #ffffff; padding: 20px; text-align: center; }}
            .header h2 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 20px; color: #333333; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; }}
            .info-table th, .info-table td {{ padding: 10px; border-bottom: 1px solid #eeeeee; text-align: left; }}
            .info-table th {{ background-color: #f9f9f9; width: 35%; color: #555555; font-weight: bold; }}
            .error-box {{ background-color: #ffeaea; border-left: 5px solid #d9534f; padding: 15px; margin-bottom: 20px; font-family: monospace; color: #a94442; white-space: pre-wrap; }}
            .log-box {{ background-color: #272822; color: #f8f8f2; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 13px; white-space: pre-wrap; overflow-x: auto; }}
            .footer {{ background-color: #f9f9f9; text-align: center; padding: 15px; font-size: 12px; color: #777777; border-top: 1px solid #eeeeee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🚨 Error Crítico en Pipeline ETL</h2>
            </div>
            
            {imagen_html}

            <div class="content">
                <p>Hola,</p>
                <p>La ejecución del proyecto <b>Agro-Gap Mendoza</b> ha sido interrumpida. A continuación, el detalle del fallo:</p>
                
                <table class="info-table">
                    <tr>
                        <th>Proyecto</th>
                        <td>Agro Justo Mendoza</td>
                    </tr>
                    <tr>
                        <th>Tarea Fallida</th>
                        <td><b>{task_id}</b></td>
                    </tr>
                    <tr>
                        <th>Fecha Ejecución</th>
                        <td>{fecha_ejecucion}</td>
                    </tr>
                </table>

                <h3>Error Exacto de Python:</h3>
                <div class="error-box">{str(excepcion)}</div>

                <h3>Últimos registros del Log local:</h3>
                <div class="log-box">{ultimas_lineas}</div>
                
                <p style="margin-top: 20px; font-size: 13px; color: #666; text-align: center;">
                    <em>Por favor, revisa la interfaz web de Airflow para el log completo.</em>
                </p>
            </div>
            <div class="footer">
                Generado automáticamente por Apache Airflow - Proyecto Agro Justo
            </div>
        </div>
    </body>
    </html>
    """

    try:
        send_email(
            to= lista_destinatarios, 
            subject=asunto, 
            html_content=cuerpo_correo
        )
        print("ALERTA: Correo enviado. Hora local configurada correctamente.")
    except Exception as e:
        print(f"ERROR FATAL: No se pudo enviar el correo vía SMTP. Detalle: {str(e)}")


# ==============================================================
# 🟢 FUNCIÓN DE ALERTA: ÉXITO
# ==============================================================
def alerta_exito_etl(**context):
    # 1. Obtener la hora local de Mendoza
    logical_date = context.get('logical_date')
    if logical_date:
        fecha_local = pendulum.instance(logical_date).in_timezone('America/Argentina/Mendoza')
        fecha_ejecucion = fecha_local.strftime("%Y-%m-%d %H:%M:%S")
    else:
        fecha_ejecucion = "Desconocida"

    # 2. Rescatar las variables dinámicas mediante XCom
    ti = context.get('ti')
    datos_resumen = ti.xcom_pull(task_ids='cargar') if ti else None
    
    # Valores por defecto en caso de que la tarea cargar no retorne el diccionario
    if not datos_resumen:
        datos_resumen = {
            "productos": "N/D",
            "sucursales": "N/D",
            "dolar_blue": "N/D"
        }

    # 3. 🟢 URL de la imagen de presentación para el correo de éxito
    url_imagen_exito = "https://github.com/nicolas2704/Agro-Justo-Mendoza/blob/main/imagenes/imagen_presentacion.png?raw=true"
    
    # Crear el bloque HTML de la imagen de presentación
    imagen_html_exito = f'''
    <div style="text-align: center; background-color: #f9f9f9; padding: 15px; border-bottom: 1px solid #eeeeee;">
        <img src="{url_imagen_exito}" alt="Presentación Agro Justo" style="max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    </div>
    '''

    # 4. Diseño HTML del correo de éxito
    asunto = "✅ ÉXITO: ETL Agro-Gap Mendoza Finalizado"
    cuerpo_correo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }}
            .container {{ max-width: 650px; margin: auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border: 1px solid #e0e0e0; }}
            .header {{ background-color: #28a745; color: #ffffff; padding: 20px; text-align: center; }}
            .header h2 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 20px; color: #333333; }}
            .summary-box {{ background-color: #e9f7ef; border-left: 5px solid #28a745; padding: 15px; margin-bottom: 20px; font-size: 16px; line-height: 1.5; color: #155724; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; }}
            .info-table th, .info-table td {{ padding: 10px; border-bottom: 1px solid #eeeeee; text-align: left; }}
            .info-table th {{ background-color: #f9f9f9; width: 40%; color: #555555; font-weight: bold; }}
            .footer {{ background-color: #f9f9f9; text-align: center; padding: 15px; font-size: 12px; color: #777777; border-top: 1px solid #eeeeee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>✅ Pipeline Ejecutado Correctamente</h2>
            </div>
            
            <!-- 🟢 IMAGEN DE PRESENTACIÓN UBICADA AL PRINCIPIO DEL CUERPO -->
            {imagen_html_exito}

            <div class="content">
                <p>Hola,</p>
                
                <div class="summary-box">
                    <strong>¡Todo listo!</strong> El ETL de Agro-Gap Mendoza finalizó correctamente sin arrojar errores. Los datos ya están disponibles para el análisis.
                </div>
                
                <h3>Resumen de la Operación:</h3>
                <table class="info-table">
                    <tr>
                        <th>Fecha de Ejecución (Mendoza)</th>
                        <td>{fecha_ejecucion}</td>
                    </tr>
                    <tr>
                        <th>Productos Actualizados</th>
                        <td><b>{datos_resumen['productos']}</b></td>
                    </tr>
                    <tr>
                        <th>Sucursales Procesadas</th>
                        <td><b>{datos_resumen['sucursales']}</b></td>
                    </tr>
                    <tr>
                        <th>Cotización Dólar Blue</th>
                        <td><b>${datos_resumen['dolar_blue']}</b></td>
                    </tr>
                </table>
            </div>
            <div class="footer">
                Generado automáticamente por Apache Airflow - Proyecto Agro Justo
            </div>
        </div>
    </body>
    </html>
    """

    # 5. Enviar el correo
    try:
        send_email(
            to=lista_destinatarios, 
            subject=asunto, 
            html_content=cuerpo_correo
        )
        print("ÉXITO: Correo de confirmación enviado correctamente.")
    except Exception as e:
        print(f"ERROR: No se pudo enviar el correo de éxito. Detalle: {str(e)}")


# ==============================================================
# 🟡 FUNCIÓN DE ALERTA: ADVERTENCIA
# ==============================================================
def alerta_brecha_extrema(productos_alerta):
    from airflow.utils.email import send_email
    
    # 1. Construir las filas de la tabla dinámicamente incluyendo la IMAGEN
    filas_html = ""
    for item in productos_alerta:
        filas_html += f"""
        <tr>
            <td style="text-align: center; vertical-align: middle;">
                <img src="{item['url_imagen']}" alt="{item['producto']}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px; border: 1px solid #ddd;">
            </td>
            <td style="vertical-align: middle;"><b>{item['producto']}</b><br><span style="font-size: 12px; color: #777;">{item['supermercado']}</span></td>
            <td style="color: #d9534f; font-weight: bold; vertical-align: middle; font-size: 16px;">{item['brecha']}%</td>
            <td style="vertical-align: middle;">${item['precio_super']}</td>
            <td style="vertical-align: middle;">${item['precio_feria']}</td>
        </tr>
        """

    # 2. Diseño HTML (Temática Naranja/Alerta)
    asunto = "⚠️ OPORTUNIDAD: Brecha de precio inusual detectada"
    cuerpo_correo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }}
            .container {{ max-width: 700px; margin: auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border: 1px solid #e0e0e0; }}
            .header {{ background-color: #f0ad4e; color: #ffffff; padding: 20px; text-align: center; }}
            .header h2 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 20px; color: #333333; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; }}
            .info-table th, .info-table td {{ padding: 10px; border-bottom: 1px solid #eeeeee; text-align: left; }}
            .info-table th {{ background-color: #f9f9f9; color: #555555; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>⚠️ Alerta de Rentabilidad Extrema (Zona Roja)</h2>
            </div>
            <div class="content">
                <p>El sistema ETL ha detectado productos con un sobreprecio en supermercados superior al <b>300%</b> respecto a la Feria de Guaymallén.</p>
                
                <table class="info-table">
                    <tr>
                        <th style="width: 60px;">Foto</th>
                        <th>Producto / Cadena</th>
                        <th>Brecha</th>
                        <th>Precio Super</th>
                        <th>Precio Feria</th>
                    </tr>
                    <!-- 🟢 Aquí inyectamos las filas generadas por el bucle -->
                    {filas_html}
                </table>
                
                <p style="font-size: 13px; color: #666; text-align: center;">Revisa el dashboard de Power BI para ver el impacto exacto por zona geográfica.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # 3. Enviar el correo
    send_email(
        to=lista_destinatarios, 
        subject=asunto, 
        html_content=cuerpo_correo
    )