import sqlite3
from core.database import get_connection
from datetime import date

def add_finance_entry(entry_type, amount, description, entry_date=None):
    if not entry_date:
        entry_date = date.today().strftime("%Y-%m-%d")
        
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO finances (entry_type, amount, description, date) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (entry_type, amount, description, entry_date))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding finance entry: {e}")
            return False
        finally:
            connection.close()
    return False

def update_finance_entry(entry_id, entry_type, amount, description, entry_date):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "UPDATE finances SET entry_type=?, amount=?, description=?, date=? WHERE id=?"
            cursor.execute(query, (entry_type, amount, description, entry_date, entry_id))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating finance: {e}")
            return False
        finally:
            connection.close()
    return False

def get_finance_by_id(entry_id):
    connection = get_connection()
    entry = None
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM finances WHERE id = ?", (entry_id,))
        entry = cursor.fetchone()
        connection.close()
    return entry

def get_all_finances(sort_by="date", order="DESC"):
    connection = get_connection()
    finances = []
    if connection:
        try:
            cursor = connection.cursor()
            query = f"SELECT id, entry_type, amount, description, date FROM finances ORDER BY {sort_by} {order}"
            cursor.execute(query)
            finances = cursor.fetchall()
        finally:
            connection.close()
    return finances

def search_finances(term, sort_by="date", order="DESC"):
    connection = get_connection()
    finances = []
    if connection:
        try:
            cursor = connection.cursor()
            query = f"""
            SELECT id, entry_type, amount, description, date 
            FROM finances 
            WHERE description LIKE ? OR entry_type LIKE ? OR date LIKE ?
            ORDER BY {sort_by} {order}
            """
            like_term = f"%{term}%"
            cursor.execute(query, (like_term, like_term, like_term))
            finances = cursor.fetchall()
        finally:
            connection.close()
    return finances

def delete_finance(entry_id):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM finances WHERE id = ?", (entry_id,))
            connection.commit()
            return True
        finally:
            connection.close()
    return False

def get_finance_summary():
    connection = get_connection()
    summary = {"income": 0.0, "expense": 0.0, "balance": 0.0}
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT entry_type, SUM(amount) FROM finances GROUP BY entry_type")
            rows = cursor.fetchall()
            for row in rows:
                if row[0] == 'income': summary["income"] = row[1] or 0.0
                elif row[0] == 'expense': summary["expense"] = row[1] or 0.0
            summary["balance"] = summary["income"] - summary["expense"]
        finally:
            connection.close()
    return summary