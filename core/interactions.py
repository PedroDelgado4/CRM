import sqlite3
from core.database import get_connection

def add_interaction(contact_id, opportunity_id, type, note, status, reminder_date):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # No enviamos date_time porque SQLite lo rellena solo con el CURRENT_TIMESTAMP
            query = """
            INSERT INTO interactions (contact_id, opportunity_id, type, note, status, reminder_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (contact_id, opportunity_id, type, note, status, reminder_date))
            connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding interaction: {e}")
            return False
        finally:
            connection.close()
    return False

def get_all_interactions(sort_by="i.id", order="DESC", type_filter=None):
    from core.database import get_connection
    connection = get_connection()
    interactions = []
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT i.id, i.note, i.type, i.date_time, i.status, i.reminder_date,
               c.full_name, o.name
        FROM interactions i
        LEFT JOIN contacts c ON i.contact_id = c.id
        LEFT JOIN opportunities o ON i.opportunity_id = o.id
        """
        params = []
        if type_filter and type_filter != "All":
            query += " WHERE i.type = ?"
            params.append(type_filter)
            
        query += f" ORDER BY {sort_by} {order}"
        cursor.execute(query, tuple(params))
        interactions = cursor.fetchall()
        connection.close()
    return interactions

def search_interactions(term, sort_by="i.id", order="DESC", type_filter=None):
    from core.database import get_connection
    connection = get_connection()
    interactions = []
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT i.id, i.note, i.type, i.date_time, i.status, i.reminder_date,
               c.full_name, o.name
        FROM interactions i
        LEFT JOIN contacts c ON i.contact_id = c.id
        LEFT JOIN opportunities o ON i.opportunity_id = o.id
        WHERE (i.note LIKE ? OR c.full_name LIKE ? OR o.name LIKE ?)
        """
        like_term = f"%{term}%"
        params = [like_term, like_term, like_term]

        if type_filter and type_filter != "All":
            query += " AND i.type = ?"
            params.append(type_filter)
            
        query += f" ORDER BY {sort_by} {order}"
        cursor.execute(query, tuple(params))
        interactions = cursor.fetchall()
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

def get_interaction_by_id(interaction_id):
    connection = get_connection()
    interaction = None
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM interactions WHERE id = ?", (interaction_id,))
        interaction = cursor.fetchone()
        connection.close()
    return interaction

def update_interaction(interaction_id, contact_id, opportunity_id, type, note, status, reminder_date):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            UPDATE interactions 
            SET contact_id=?, opportunity_id=?, type=?, note=?, status=?, reminder_date=?
            WHERE id=?
            """
            cursor.execute(query, (contact_id, opportunity_id, type, note, status, reminder_date, interaction_id))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating interaction: {e}")
            return False
        finally:
            connection.close()
    return False

def link_product_to_interaction(inter_id, product_id):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT OR REPLACE INTO interaction_products (interaction_id, product_id) VALUES (?, ?)"
            cursor.execute(query, (inter_id, product_id))
            connection.commit()
            return True
        finally:
            connection.close()
    return False

def unlink_all_products_from_interaction(inter_id):
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM interaction_products WHERE interaction_id = ?", (inter_id,))
        connection.commit()
        connection.close()

def get_interaction_products(inter_id):
    connection = get_connection()
    products = []
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT p.id, p.name 
        FROM products p
        JOIN interaction_products ip ON p.id = ip.product_id
        WHERE ip.interaction_id = ?
        """
        cursor.execute(query, (inter_id,))
        products = cursor.fetchall()
        connection.close()
    return products