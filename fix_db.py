import sqlite3

conn = sqlite3.connect('crm_data.db')
c = conn.cursor()

# Borramos la tabla defectuosa y la recreamos con todas las columnas
c.execute("DROP TABLE IF EXISTS opportunity_products;")
c.execute("""
CREATE TABLE opportunity_products (
    opportunity_id INTEGER,
    product_id INTEGER,
    quantity INTEGER DEFAULT 1,
    unit_price REAL,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities (id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
    PRIMARY KEY (opportunity_id, product_id)
)
""")
conn.commit()
conn.close()
print("¡Tabla opportunity_products arreglada!")