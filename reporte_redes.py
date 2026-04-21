import csv
from sqlalchemy import create_engine, text
from datetime import datetime
import os

DB_URL = "postgresql://admin_dev:PasswordSeguro123!@localhost:5432/db_extraccion"
CHUNK_SIZE = 5000 

def generar_reporte_optimizado():
    ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
    fecha = datetime.now().strftime("%Y_%m_%d_%H%M") # Agregamos hora y minuto para notar cambios
    nombre_archivo = os.path.join(ruta_carpeta, f"reporte_telefonia_{fecha}.csv")
    
    try:
        engine = create_engine(DB_URL)
        
        with engine.connect() as conn:
            
            result = conn.execution_options(stream_results=True).execute(text("SELECT * FROM logs_telefonia"))
            
            with open(nombre_archivo, 'w', newline='', encoding='utf-8-sig') as f:
                
                writer = csv.writer(f, delimiter=';')
                writer.writerow(result.keys())
                contador = 0
                
                while True:
                    rows = result.fetchmany(CHUNK_SIZE)
                    if not rows:
                        break
                    writer.writerows(rows)
                    contador += len(rows)
                    

    except Exception as e:
        print(e)

if __name__ == "__main__":
    generar_reporte_optimizado()