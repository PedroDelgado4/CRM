import sqlite3
from core.database import get_connection
import webbrowser

def add_contact(full_name, company_id, is_vip, email, phone, position, linkedin, assigned_to=None):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO contacts (full_name, company_id, is_vip, email, phone, position, linkedin, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (full_name, company_id, is_vip, email, phone, position, linkedin, assigned_to))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding contact: {e}")
            return False
        finally:
            connection.close()
    return False

def get_all_contacts(sort_by="c.full_name", order="ASC"):
    connection = get_connection()
    contacts = []
    if connection:
        try:
            cursor = connection.cursor()
            query = f"""
            SELECT c.id, c.full_name, comp.name, c.is_vip, c.email, c.phone, c.position, c.linkedin, c.assigned_to
            FROM contacts c
            LEFT JOIN companies comp ON c.company_id = comp.id
            ORDER BY {sort_by} {order}
            """
            cursor.execute(query)
            contacts = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching contacts: {e}")
        finally:
            connection.close()
    return contacts

def search_contacts(term, sort_by="c.full_name", order="ASC"):
    connection = get_connection()
    contacts = []
    if connection:
        try:
            cursor = connection.cursor()
            query = f""" 
            SELECT c.id, c.full_name, comp.name, c.is_vip, c.email, c.phone, c.position, c.linkedin, c.assigned_to 
            FROM contacts c
            LEFT JOIN companies comp ON c.company_id = comp.id
            WHERE c.full_name LIKE ? OR comp.name LIKE ? 
            ORDER BY {sort_by} {order}
            """
            filter_item = f"%{term}%"
            cursor.execute(query, (filter_item, filter_item))
            contacts = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching contacts: {e}")
        finally:
            connection.close()
    return contacts

def delete_contact(contact_id):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting contact: {e}")
            return False
        finally:
            connection.close()
    return False    

def assign_responsable(contact_id, user_id):
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE contacts SET assigned_to = ? WHERE id = ?", (user_id, contact_id))
        connection.commit()
        connection.close()
        return True
    return False

# MODIFICADO: Añadido sort_by y order
def get_contacts_by_filter(is_vip=None, user_id=None, search_term=None, sort_by="c.full_name", order="ASC"):
    connection = get_connection()
    contacts = []
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT c.id, c.full_name, comp.name, c.is_vip, c.email, c.phone, c.position, c.linkedin, c.assigned_to 
        FROM contacts c
        LEFT JOIN companies comp ON c.company_id = comp.id
        WHERE 1=1
        """
        params = []

        if is_vip is not None:
            query += " AND c.is_vip = ?"
            params.append(is_vip)
        if user_id:
            query += " AND c.assigned_to = ?"
            params.append(user_id)
        if search_term:
            query += " AND (c.full_name LIKE ? OR comp.name LIKE ?)"
            term = f"%{search_term}%"
            params.extend([term, term])

        # Inyectamos el orden al final de la consulta
        query += f" ORDER BY {sort_by} {order}"

        try:
            cursor.execute(query, params)
            contacts = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error filtering contacts: {e}")
        finally:
            connection.close()
    return contacts

def get_today_reminders(user_id):
    connection = get_connection()
    reminders = []
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT c.full_name, comp.name, i.note
        FROM interactions i
        JOIN contacts c ON i.contact_id = c.id
        LEFT JOIN companies comp ON c.company_id = comp.id
        WHERE c.assigned_to = ? AND i.reminder_date = DATE('now')
        """
        cursor.execute(query, (user_id,))
        reminders = cursor.fetchall()
        connection.close()
    return reminders

def open_email(email_address):
    if email_address and email_address != "-":
        webbrowser.open(f"mailto:{email_address}")

def add_interaction(contact_id, note, reminder_date=None, opportunity_id=None):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO interactions (contact_id, note, date_time, reminder_date, opportunity_id) VALUES (?, ?, DATE('now'), ?, ?)"
            cursor.execute(query, (contact_id, note, reminder_date, opportunity_id))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving interaction: {e}")
            return False
        finally:
            connection.close()
    return False