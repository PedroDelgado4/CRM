import sqlite3
from core.database import get_connection

def add_interaction(contact_id, opportunity_id, interaction_type, note, status, reminder_date):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # No enviamos date_time porque SQLite lo rellena solo con el CURRENT_TIMESTAMP
            query = """
            INSERT INTO interactions (contact_id, opportunity_id, type, note, status, reminder_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (contact_id, opportunity_id, interaction_type, note, status, reminder_date))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding interaction: {e}")
            return False
        finally:
            connection.close()
    return False

def get_all_interactions(sort_by="i.date_time", order="DESC"):
    # Por defecto ordenamos por fecha descendente (las más nuevas primero)
    connection = get_connection()
    interactions = []
    if connection:
        try:
            cursor = connection.cursor()
            query = f"""
            SELECT i.id, i.note, i.type, i.date_time, i.status, i.reminder_date, c.full_name, o.name
            FROM interactions i
            LEFT JOIN contacts c ON i.contact_id = c.id
            LEFT JOIN opportunities o ON i.opportunity_id = o.id
            ORDER BY {sort_by} {order}
            """
            cursor.execute(query)
            interactions = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching interactions: {e}")
        finally:
            connection.close()
    return interactions

def search_interactions(term, sort_by="i.date_time", order="DESC"):
    connection = get_connection()
    interactions = []
    if connection:
        try:
            cursor = connection.cursor()
            # busca en la nota, el tipo, el estado, el nombre del contacto o de la oportunidad
            query = f"""
            SELECT i.id, i.note, i.type, i.date_time, i.status, i.reminder_date, c.full_name, o.name
            FROM interactions i
            LEFT JOIN contacts c ON i.contact_id = c.id
            LEFT JOIN opportunities o ON i.opportunity_id = o.id
            WHERE i.note LIKE ? OR i.type LIKE ? OR i.status LIKE ? OR c.full_name LIKE ? OR o.name LIKE ?
            ORDER BY {sort_by} {order}
            """
            like_term = f"%{term}%"
            cursor.execute(query, (like_term, like_term, like_term, like_term, like_term))
            interactions = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching interactions: {e}")
        finally:
            connection.close()
    return interactions

def delete_interaction(interaction_id):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM interactions WHERE id = ?", (interaction_id,))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting interaction: {e}")
            return False
        finally:
            connection.close()
    return False