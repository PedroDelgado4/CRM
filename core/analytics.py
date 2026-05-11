import sqlite3
import os
import webbrowser
from core.database import get_connection

def get_sales_data():
    conn = get_connection()
    data = {
        "total_revenue": 0.0,
        "avg_sale": 0.0,
        "products_sold": []
    }
    if not conn: return data

    try:
        cursor = conn.cursor()
        
        # 1. Total y Promedio de Oportunidades Ganadas
        cursor.execute("SELECT SUM(estimated_value), AVG(estimated_value) FROM opportunities WHERE status = 'closed_won'")
        row = cursor.fetchone()
        data["total_revenue"] = row[0] or 0.0
        data["avg_sale"] = row[1] or 0.0

        # 2. Conteo de Productos Vendidos (solo en Oportunidades Ganadas)
        query = """
        SELECT p.name, COUNT(op.product_id) as total_sold
        FROM opportunity_products op
        JOIN opportunities o ON op.opportunity_id = o.id
        JOIN products p ON op.product_id = p.id
        WHERE o.status = 'closed_won'
        GROUP BY p.id
        ORDER BY total_sold DESC
        """
        cursor.execute(query)
        data["products_sold"] = cursor.fetchall() # Lista de tuplas: [("Producto A", 3), ("Producto B", 1)]
    except sqlite3.Error as e:
        print(f"Error fetching analytics: {e}")
    finally:
        conn.close()

    return data

def generate_html_report():
    data = get_sales_data()

    # Preparamos los datos para inyectarlos en el gráfico de JavaScript
    labels = [item[0] for item in data["products_sold"]]
    values = [item[1] for item in data["products_sold"]]

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Sales Analytics - CRM FDT</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #f4f4f9; padding: 30px; margin: 0; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #2b2b2b; padding: 30px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.5); }}
            h1 {{ color: #2E8D1B; text-align: center; border-bottom: 2px solid #3F3F3F; padding-bottom: 15px; margin-bottom: 30px; }}
            .stats {{ display: flex; justify-content: space-between; margin-bottom: 40px; gap: 20px; }}
            .stat-box {{ background: #3F3F3F; padding: 25px; border-radius: 10px; text-align: center; flex: 1; border-top: 4px solid #2E8D1B; }}
            .stat-box h3 {{ margin: 0; font-size: 1.1em; color: #D9D9D9; text-transform: uppercase; letter-spacing: 1px; }}
            .stat-box p {{ margin: 15px 0 0 0; font-size: 2.2em; font-weight: bold; color: #fff; }}
            .chart-container {{ background: #3F3F3F; padding: 20px; border-radius: 10px; }}
            h2 {{ color: #D9D9D9; text-align: center; margin-bottom: 20px; font-weight: normal; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Business Sales Report</h1>
            
            <div class="stats">
                <div class="stat-box">
                    <h3>Total Revenue (Closed Won)</h3>
                    <p>{data['total_revenue']:,.2f} €</p>
                </div>
                <div class="stat-box">
                    <h3>Average Sale Value</h3>
                    <p>{data['avg_sale']:,.2f} €</p>
                </div>
            </div>

            <div class="chart-container">
                <h2>Product Sales Distribution</h2>
                <canvas id="salesChart"></canvas>
            </div>
        </div>

        <script>
            const ctx = document.getElementById('salesChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {labels},
                    datasets: [{{
                        label: 'Units Sold',
                        data: {values},
                        backgroundColor: '#2E8D1B',
                        borderColor: '#246B15',
                        borderWidth: 1,
                        borderRadius: 5
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{ 
                            beginAtZero: true, 
                            ticks: {{ stepSize: 1, color: '#D9D9D9' }},
                            grid: {{ color: '#555' }}
                        }},
                        x: {{
                            ticks: {{ color: '#D9D9D9' }},
                            grid: {{ display: false }}
                        }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#D9D9D9' }} }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """

    # Guardamos el archivo y lo abrimos automáticamente
    file_path = os.path.abspath("sales_report.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Report generated successfully!")
    webbrowser.open('file://' + file_path)

# Esto permite ejecutar el script directamente para probarlo
if __name__ == "__main__":
    generate_html_report()