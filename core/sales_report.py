import csv
import os
from core.database import get_connection

def generate_sales_csv(filepath="sales_data.csv"):
    """
    Extrae las ventas (Opportunities en 'closed_won'), cruzando datos con 
    clientes y productos, y genera el archivo CSV requerido por el ejercicio.
    """
    conn = get_connection()
    if not conn: 
        return False
        
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                o.expected_close_date AS Date,
                COALESCE(c.full_name, comp.name, 'Unknown Client') AS Client,
                p.name AS Product,
                p.min_price AS Price 
            FROM opportunities o
            LEFT JOIN contacts c ON o.contact_id = c.id
            LEFT JOIN companies comp ON o.company_id = comp.id
            JOIN opportunity_products op ON o.id = op.opportunity_id
            JOIN products p ON op.product_id = p.id
            WHERE LOWER(o.status) = 'closed_won'
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Generamos el CSV en la ruta especificada
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Cabeceras exactas que pide el ejercicio
            writer.writerow(["Date", "Client", "Product", "Price"])
            
            # Escribimos todas las filas de datos
            writer.writerows(rows)
            
        return True
        
    except Exception as e:
        print(f"Error generating sales CSV: {e}")
        return False
    finally:
        conn.close()