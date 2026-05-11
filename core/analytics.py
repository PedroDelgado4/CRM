import sqlite3
import os
import webbrowser
from core.database import get_connection

def get_advanced_stats():
    conn = get_connection()
    stats = {"total_rev": 0, "win_rate": 0, "weighted_pipe": 0, "labels": [], "values": []}
    if not conn: return stats
    
    cursor = conn.cursor()
    # 1. Ingresos totales (Won)
    cursor.execute("SELECT SUM(estimated_value) FROM opportunities WHERE status = 'closed_won'")
    stats["total_rev"] = cursor.fetchone()[0] or 0.0

    # 2. Win Rate (Tasa de conversión)
    cursor.execute("SELECT COUNT(*) FROM opportunities WHERE status = 'closed_won'")
    won = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM opportunities WHERE status IN ('closed_won', 'closed_lost')")
    total = cursor.fetchone()[0] or 0
    stats["win_rate"] = (won / total * 100) if total > 0 else 0

    # 3. Pipeline Ponderado (Valor * Probabilidad según etapa)
    query = """
    SELECT SUM(CASE 
        WHEN status = 'qualification' THEN estimated_value * 0.1
        WHEN status = 'proposal' THEN estimated_value * 0.3
        WHEN status = 'evaluation' THEN estimated_value * 0.5
        WHEN status = 'negotiation' THEN estimated_value * 0.8
        ELSE 0 END) FROM opportunities WHERE status NOT IN ('closed_won', 'closed_lost')
    """
    cursor.execute(query)
    stats["weighted_pipe"] = cursor.fetchone()[0] or 0.0

    # 4. Datos para el gráfico de barras
    cursor.execute("""
        SELECT p.name, COUNT(op.product_id) 
        FROM opportunity_products op 
        JOIN products p ON op.product_id = p.id 
        GROUP BY p.id
    """)
    rows = cursor.fetchall()
    stats["labels"] = [r[0] for r in rows]
    stats["values"] = [r[1] for r in rows]
    
    conn.close()
    return stats

def generate_html_report():
    data = get_advanced_stats()
    
    # El HTML con el estilo: Negro y Verde Neón
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sales Intelligence Report</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background: #000; color: #fff; font-family: sans-serif; padding: 40px; }}
            h1 {{ color: #deff9a; border-bottom: 1px solid #333; padding-bottom: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 40px 0; }}
            .card {{ background: #1a1a1a; padding: 25px; border-radius: 15px; border: 1px solid #deff9a33; text-align: center; }}
            .card h3 {{ color: #deff9a; margin: 0; font-size: 14px; text-transform: uppercase; }}
            .card p {{ font-size: 32px; font-weight: bold; margin: 10px 0 0; }}
            .chart-box {{ background: #1a1a1a; padding: 30px; border-radius: 15px; }}
        </style>
    </head>
    <body>
        <h1>Business <span>Intelligence</span> Report</h1>
        <div class="grid">
            <div class="card"><h3>Total Revenue</h3><p>{data['total_rev']:,.2f} €</p></div>
            <div class="card"><h3>Win Rate</h3><p>{data['win_rate']:.1f}%</p></div>
            <div class="card"><h3>Weighted Pipeline</h3><p>{data['weighted_pipe']:,.2f} €</p></div>
        </div>
        <div class="chart-box">
            <canvas id="myChart"></canvas>
        </div>
        <script>
            new Chart(document.getElementById('myChart'), {{
                type: 'bar',
                data: {{
                    labels: {data['labels']},
                    datasets: [{{
                        label: 'Units Sold',
                        data: {data['values']},
                        backgroundColor: '#deff9a'
                    }}]
                }},
                options: {{ 
                    scales: {{ 
                        y: {{ grid: {{ color: '#333' }}, ticks: {{ color: '#fff' }} }},
                        x: {{ ticks: {{ color: '#fff' }} }}
                    }},
                    plugins: {{ legend: {{ labels: {{ color: '#fff' }} }} }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    path = os.path.abspath("intelligence_report.html")
    with open(path, "w", encoding="utf-8") as f: 
        f.write(html_template)
    webbrowser.open("file://" + path)

def get_cross_selling_suggestions():
    conn = get_connection()
    suggestions = []
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            SELECT comp.id, comp.name, COUNT(c.id) as contact_count
            FROM companies comp
            JOIN contacts c ON comp.id = c.company_id
            WHERE comp.id NOT IN (
                SELECT company_id FROM opportunities 
                WHERE status IN ('qualification', 'proposal', 'evaluation', 'negotiation')
                AND company_id IS NOT NULL
            )
            GROUP BY comp.id
            ORDER BY contact_count DESC
            LIMIT 5
            """
            cursor.execute(query)
            suggestions = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching suggestions: {e}")
        finally:
            conn.close()
    return suggestions