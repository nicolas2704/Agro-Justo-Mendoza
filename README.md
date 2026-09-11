# 🍎🥦🥕 Data Engineering & BI para Mercado Frutihortícola 🍅🥔🧅 – Agro Justo Mendoza (Agro-Gap)

![Data Engineering](https://img.shields.io/badge/Data%20Engineering-Pipeline-blue)
![Data Analysis](https://img.shields.io/badge/Data%20Analysis-Mendoza-green)
![Python](https://img.shields.io/badge/Language-Python-blue)
![Docker](https://img.shields.io/badge/Container-Docker-cyan)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![Airflow](https://img.shields.io/badge/Orchestration-Airflow-red)
![Make](https://img.shields.io/badge/Automation-Make-purple)
![Excel](https://img.shields.io/badge/Spreadsheet-Excel-brightgreen)
![PowerBI](https://img.shields.io/badge/Dashboard-PowerBI-yellow)

---

![Presentación Agro Justo Mendoza](https://github.com/nicolas2704/Agro-Justo-Mendoza/blob/main/imagenes/imagen_presentacion.png?raw=true)

# 📊 Monitoreo económico y análisis estratégico de precios

El proyecto **Agro Justo Mendoza** ofrece una solución integral de ingeniería, análisis de datos y negocio aplicada a la economía real, abordando una problemática estructural que no había sido resuelta hasta el momento en la provincia. 

Consiste en un sistema automatizado End-to-End que expone semanalmente la brecha entre lo que se paga en el mercado mayorista y lo que se cobra en las góndolas de los supermercados mendocinos.

---

# 🚨 El Problema de Negocio

El mercado frutihortícola sufre de una grave falta de transparencia en la formación de precios. Entre el punto de origen mayorista y las góndolas de los grandes supermercados, los precios sufren distorsiones que no siempre responden a costos logísticos, sino a márgenes especulativos.

Las principales barreras y consecuencias son:
- 🛒 **Asimetría de información:** El consumidor final rara vez conoce el precio real al que se comercializan los alimentos en su etapa mayorista.
- 📉 **Falta de herramientas:** Pequeños comerciantes y analistas carecen de un termómetro rápido para entender la inflación encubierta.
- 💰 **Especulación comercial:** Aumentos irracionales de precios que afectan el costo de vida.

> Los consumidores y comerciantes **no cuentan con información clara y centralizada para tomar decisiones de compra inteligentes frente a la volatilidad del mercado.**


https://github.com/user-attachments/assets/c6dc6c20-4611-4667-8e30-4ff31a0bc3a7

---

# 🎯 Solución y Objetivo

El proyecto cuantifica matemáticamente esta distorsión, transformando la queja anecdótica sobre el costo de vida en un **indicador duro, auditable y basado en datos reales**.

**Objetivo del Proyecto:**
Desarrollar un pipeline de datos *End-to-End* para monitorear, cuantificar y alertar sobre la brecha de rentabilidad y la especulación de precios. Este sistema de vigilancia económica democratiza la información, pasando de un escenario de control minorista absoluto, a empoderar al consumidor final con datos para decisiones estratégicas.

---

# 🏗️ Arquitectura y Flujo de Datos (ETL)
![Arquitectura Agro Justo Mendoza]( https://github.com/nicolas2704/Agro-Justo-Mendoza/blob/main/imagenes/Diagrama_Agro_Justo-Mza.png?raw=true)

Se construyó un contenedor de **Docker** para facilitar la arquitectura, permitiendo correr el orquestador **Apache Airflow** de forma aislada y automatizando el flujo de datos (DAGs) mediante scripts en **Python**.

> **Visualización de la Arquitectura:**
> ![Arquitectura del Proyecto](./ruta_a_tu_imagen_arquitectura.png) 
> *(Esquema topológico del pipeline de datos)*

### 1️⃣ Orquestación y Extracción (Ingesta Dual)
El ciclo inicia mediante un DAG programado con ejecución semanal. Se extrae información de múltiples fuentes:
*   **Procesamiento de PDFs (IA):** Uso de Google Gemini para extraer con precisión datos de reportes no estructurados del Gobierno de Mendoza.
*   **Web Scraping:** Pandas y un archivo maestro (Excel) para capturar precios en páginas web oficiales de supermercados.
*   **Consumo de API:** Integración financiera para obtener el valor actualizado del dólar.

### 2️⃣ Transformación y Limpieza
Los datos crudos son procesados mediante **Pandas**. El flujo estandariza la nomenclatura, gestiona metadatos y genera *Smart Keys* para garantizar un cruce exacto entre fechas y sucursales. 
*   **Regla de Negocio:** El sistema detecta brechas de precio extremas (superiores al 300%) como disparador de anomalías.

### 3️⃣ Almacenamiento y Modelado Analítico
Carga incremental semanal en una base de datos **PostgreSQL** en la nube. El repositorio maximiza el rendimiento analítico mediante un diseño estructurado que aísla el contexto (dimensiones) y centraliza las métricas (hechos).

### 4️⃣ Trazabilidad, Automatización y Alertas (Make)
El flujo mantiene auditoría estricta mediante logs en `.txt`. La arquitectura orientada a eventos integra **Make.com** para reaccionar a la ingesta:
*   **Alertas Técnicas:** Correos por ejecución Exitosa o Errónea.
*   **Alertas de Negocio:** Notificación de brechas especulativas (≥300%).
*   **Reportes PDF Automatizados:** Consulta del *Top 5 de sobreprecios* y reporte de *Inflación Minorista* distribuidos vía Telegram y Gmail.

---

# 🧰 Tecnologías Utilizadas
 
<p align="left">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40" title="Python"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg" width="40" title="Pandas"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" width="40" title="PostgreSQL"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="40" title="Docker"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/apacheairflow/apacheairflow-original.svg" width="40" title="Airflow"/>
<img src="https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg" width="40" title="Power BI"/>
<img src="https://img.icons8.com/color/48/microsoft-excel-2019.png" width="40" title="Excel"/>
<img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" width="40" title="Telegram"/>
</p>

*   **Lenguajes & Procesamiento:** Python, Pandas.
*   **Orquestación & Infraestructura:** Apache Airflow, Docker.
*   **Base de Datos & Modelado:** PostgreSQL, SQL.
*   **Automatización & Alertas:** Make.com, Telegram Bot API, Gmail.
*   **Inteligencia Artificial:** Google Gemini.
*   **Visualización & BI:** Power BI, DAX, Excel.
 
---
# 🗄 Modelo de Datos

Se diseñó un modelo en Estrella analítico relacional optimizado para consultas eficientes y consumo en herramientas de BI, estructurado en **5 tablas principales**:

*   **Tablas de Hechos (2):** `monitoreo_precios`, `cotizaciones_divisas`.
*   **Tablas de Dimensiones (3):** `calendario`, `sucursales`, `productos`.

---

# 📊 Dashboard de Business Intelligence

La interfaz final de Power BI traduce millones de registros en métricas accionables, destacando anomalías y tendencias temporales.

### 📌 KPIs Principales
- **Brecha Promedio Global:** Sobreprecio general de la canasta (*Ej: 100% indica que el super cuesta el doble que la feria*).
- **Producto Alerta:** Muestra el producto con mayor especulación semanal (outliers a evitar en góndola).
- **Ahorro Canasta:** Cuantificación monetaria del ahorro al comprar directo en el mercado mayorista.
- **Supermercado Especulador:** Cadena minorista con la política de precios más alta de la semana.

### 📈 Análisis Gráfico
- **Ranking de Especulación:** Matriz de barras evaluando la agresividad de precios por cadena.
- **Evolución Histórica y por Producto:** Gráficos de líneas bivariados para detectar inflación vs. oportunismo comercial.
- **Detección de Outliers:** Gráfico de dispersión para aislar el sobreprecio atípico.
- **Catálogo y Auditoría Analítica:** Semáforo visual (verde = precio justo / rojo = alerta crítica).

![Dashboard General](./ruta_a_tu_imagen_dashboard_1.png)
![Análisis Detalle](./ruta_a_tu_imagen_dashboard_2.png)

---

# 💡 Recomendaciones y Toma de Decisiones

Este sistema de inteligencia empodera a distintos actores del mercado:

**Para el Sector Gastronómico y Compras B2B:**
*   **Alerta de Sustitución:** Ante una brecha irracional, permite cambiar de proveedor o ajustar el menú semanal.
*   **Timing de Compra:** Descubrimiento de patrones estacionales para compras por volumen en pisos históricos.

**Para el Sector Productivo y Políticas Públicas:**
*   **Evidencia de Especulación:** Datos duros que demuestran que el productor primario no es responsable de la inflación de frescos.
*   **Poder de Negociación:** Herramientas analíticas para justificar ferias directas, regulaciones o incentivos logísticos.

---

## 👥 Integrantes

- **Nicolás Hernán Montuelle**  
  <a href="https://www.linkedin.com/in/nicolasmontuelle06/" target="_blank">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg" width="25"/>
  </

