import csv
import os
import webbrowser
from core.database import get_connection
from core.sales_report import generate_sales_csv

def get_cross_selling_suggestions():
    """
    Busca empresas que tienen contactos registrados pero NINGUNA oportunidad activa.
    Devuelve: Lista de tuplas (id_empresa, nombre_empresa, numero_de_contactos)
    """
    conn = get_connection()
    suggestions = []
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT comp.id, comp.name, COUNT(c.id)
                FROM companies comp
                JOIN contacts c ON comp.id = c.company_id
                LEFT JOIN opportunities o ON comp.id = o.company_id AND LOWER(o.status) NOT IN ('closed_won', 'closed_lost')
                WHERE o.id IS NULL
                GROUP BY comp.id, comp.name
                HAVING COUNT(c.id) > 0
            """
            cursor.execute(query)
            suggestions = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching cross-selling suggestions: {e}")
        finally:
            conn.close()
    return suggestions

def generate_html_report(csv_filepath="sales_data.csv", output_html="sales_report.html"):
    """
    Lee el archivo CSV de ventas, calcula métricas clave y genera
    un informe HTML interactivo con un gráfico usando Chart.js.
    """
    # 1. Por seguridad, nos aseguramos de que el CSV existe
    generate_sales_csv(csv_filepath)

    if not os.path.exists(csv_filepath):
        print("Error: El archivo CSV no se pudo generar ni encontrar.")
        return False

    # 2. Variables para nuestros cálculos matemáticos
    total_sales = 0.0
    sales_count = 0
    product_totals = {}

    # 3. LECTURA DEL CSV
    try:
        with open(csv_filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    price = float(row["Price"])
                    product = row["Product"]
                    
                    total_sales += price
                    sales_count += 1
                    
                    # Totales por producto
                    if product in product_totals:
                        product_totals[product] += price
                    else:
                        product_totals[product] = price
                except ValueError:
                    continue 
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False

    # 4. Cálculo del promedio de ventas
    average_sale = (total_sales / sales_count) if sales_count > 0 else 0.0

    # 5. Preparar datos para el gráfico
    labels = list(product_totals.keys())
    data = list(product_totals.values())

    # 6. PLANTILLA HTML 
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CRM Detailed Sales Report</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ 
                background-color: #050505; 
                color: white; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                padding: 40px; 
                margin: 0;
            }}
            h1 {{ 
                color: #DEFF9A; 
                text-align: center; 
                margin-bottom: 40px; 
                font-size: 32px; 
                text-transform: uppercase; 
                letter-spacing: 2px; 
            }}
            .metrics-container {{ 
                display: flex; 
                justify-content: space-around; 
                margin-bottom: 50px; 
                max-width: 1000px;
                margin-left: auto;
                margin-right: auto;
            }}
            .metric-card {{ 
                background-color: #151515; 
                border: 1px solid #333; 
                border-radius: 12px; 
                padding: 25px; 
                width: 30%; 
                text-align: center; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
            }}
            .metric-title {{ 
                color: #D9D9D9; 
                font-size: 14px; 
                margin-bottom: 10px; 
                text-transform: uppercase; 
                letter-spacing: 1px;
            }}
            .metric-value {{ 
                color: #DEFF9A; 
                font-size: 32px; 
                font-weight: bold; 
            }}
            .chart-container {{ 
                background-color: #151515; 
                border: 1px solid #333; 
                border-radius: 12px; 
                padding: 30px; 
                margin: 0 auto; 
                max-width: 940px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
            }}
        </style>
    </head>
    <body>
        <h1>SALES PERFORMANCE REPORT</h1>
        
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-title">Total Revenue</div>
                <div class="metric-value">{total_sales:,.2f} €</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Total Sales (Units)</div>
                <div class="metric-value">{sales_count}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Average Sale Value</div>
                <div class="metric-value">{average_sale:,.2f} €</div>
            </div>
        </div>

        <div class="chart-container">
            <canvas id="salesChart"></canvas>
        </div>

        <script>
            const ctx = document.getElementById('salesChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {labels},
                    datasets: [{{
                        label: 'Revenue by Product (€)',
                        data: {data},
                        backgroundColor: '#DEFF9A',
                        borderColor: '#050505',
                        borderWidth: 2,
                        borderRadius: 4
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            grid: {{ color: '#333' }},
                            ticks: {{ color: '#D9D9D9', font: {{ size: 14 }} }}
                        }},
                        x: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '#D9D9D9', font: {{ size: 14 }} }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: 'white', font: {{ size: 16 }} }}
                        }},
                        tooltip: {{
                            backgroundColor: '#050505',
                            titleColor: '#DEFF9A',
                            bodyColor: 'white',
                            borderColor: '#333',
                            borderWidth: 1
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """

    # 7. Guardar el archivo HTML y abrirlo en el navegador
    try:
        with open(output_html, "w", encoding="utf-8") as file:
            file.write(html_content)
        
        webbrowser.open('file://' + os.path.realpath(output_html))
        return True
    except Exception as e:
        print(f"Error generating HTML: {e}")
        return False