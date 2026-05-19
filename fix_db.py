from core.database import get_connection

def patch_database():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Añadimos la columna faltante a la tabla opportunities
            cursor.execute("ALTER TABLE opportunities ADD COLUMN last_contact TEXT")
            conn.commit()
            print("✅ Columna 'last_contact' añadida con éxito a la base de datos.")
        except Exception as e:
            print(f"Error (o la columna ya existía): {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    patch_database()