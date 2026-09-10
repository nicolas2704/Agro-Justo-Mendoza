import pandas as pd
import random
import time
import requests

# FUNCIÓN DE SCRAPING
def obtener_precio_web(supermercado, precios_coto, id_producto=None, dataframe_url=None, sku_id=None):
    supermercado_lower = str(supermercado).lower()

    # ======================================================
    # ARQUITECTURAS VTEX (VÍA API REST)
    # Soporta: Chango Más, Vea, Jumbo, Carrefour
    # ======================================================
    if any(sup in supermercado_lower for sup in ["chango", "masonline", "vea", "jumbo", "carrefour"]):
        
        # 1. Validación de seguridad para la API
        if pd.isna(sku_id) or not sku_id:
            print(f"  -> Omitiendo API: Falta SKU para {supermercado}")
            return None
            
        # 2. Definimos el dominio base dinámicamente
        if "chango" in supermercado_lower or "masonline" in supermercado_lower:
            dominio = "https://www.masonline.com.ar"
        elif "vea" in supermercado_lower:
            dominio = "https://www.vea.com.ar"
        elif "jumbo" in supermercado_lower:
            dominio = "https://www.jumbo.com.ar"
        elif "carrefour" in supermercado_lower:
            dominio = "https://www.carrefour.com.ar"

        url_api = f"{dominio}/api/catalog_system/pub/products/search?fq=skuId:{int(sku_id)}"
        
        # 3. Headers Anti-Bot (Header Spoofing)
        headers_api = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': f"{dominio}/", 
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }

        try:
            # Pausa humana aleatoria (vital para Carrefour)
            time.sleep(random.uniform(2.5, 4.5)) 
            
            response = requests.get(url_api, headers=headers_api, timeout=15)
            
            if response.status_code == 200:
                datos = response.json()
                
                # Validamos que el producto exista
                if len(datos) > 0:
                    for item in datos[0]['items']:
                        if str(item['itemId']) == str(int(sku_id)):
                            # Ruta estándar de VTEX hacia el precio
                            precio_real = item['sellers'][0]['commertialOffer']['Price']
                            return float(precio_real)
            else:
                print(f"  -> Error HTTP {response.status_code} en la API de {supermercado}")
                
        except Exception as e:
            print(f"  -> Error procesando API en {supermercado}: {e}")
            return None

    # ======================================================
    # ARQUITECTURA COTO (Búsqueda local en DataFrame)
    # ====================================================== 
    elif "coto" in supermercado_lower:
        if pd.isna(id_producto) or not id_producto:
            print(f"  -> Omitiendo Coto: Falta SKU")
            return None
        
        if precios_coto is None:
            print(f"  -> Error: No se proporcionó el DataFrame de precios de Coto.")
            return None
            
        try:
            # Homologamos el SKU a entero para evitar problemas de tipo (ej: 1234 vs "1234")
            id_buscado = int(id_producto)
            
            # NOTA: Asegúrate de cambiar 'sku_id' y 'precio' por los nombres reales de tus columnas de Excel
            fila_producto = precios_coto[precios_coto['indice'] == id_buscado]
            
            if not fila_producto.empty:
                # Extraemos el valor de la columna de precio
                precio_real = fila_producto['precio'].values[0]
                return float(precio_real)
            else:
                print(f"  -> SKU {id_buscado} no encontrado en el archivo de Coto")
                return None
                
        except Exception as e:
            print(f"  -> Error buscando el SKU {id_producto} en el DataFrame de Coto: {e}")
            return None
                
    # Si el supermercado no coincide con ninguno de los programados
    else:
        print(f"  -> Supermercado no configurado en el enrutador: {supermercado}")
        
    return None