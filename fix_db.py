from core.database import get_connection

def patch():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Añadimos la columna. Por defecto 1 (Activo)
            cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
            conn.commit()
            print("✅ Columna 'is_active' añadida con éxito.")
        except Exception as e:
            print(f"Error o la columna ya existía: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    patch()