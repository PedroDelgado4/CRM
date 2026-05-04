import sqlite3
from core.database import get_connection

def add_opportunity(name, status, priority, estimated_value, proposal_deadline, expected_close_date, contact_id, company_id, assigned_to):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO opportunities (name, status, priority, estimated_value, proposal_deadline, expected_close_date, contact_id, company_id, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (name, status, priority, estimated_value, proposal_deadline, expected_close_date, contact_id, company_id, assigned_to))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding opportunity: {e}")
            return False
        finally:
            connection.close()
    return False

def get_all_opportunities(sort_by="o.name", order="ASC"):
    connection = get_connection()
    opps = []
    if connection:
        try:
            cursor = connection.cursor()
            query = f"""
            SELECT o.id, o.name, o.status, o.priority, o.estimated_value, o.proposal_deadline, o.expected_close_date, c.full_name, comp.name, u.username
            FROM opportunities o
            LEFT JOIN contacts c ON o.contact_id = c.id
            LEFT JOIN companies comp ON o.company_id = comp.id
            LEFT JOIN users u ON o.assigned_to = u.id
            ORDER BY {sort_by} {order}
            """
            cursor.execute(query)
            opps = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching opportunities: {e}")
        finally:
            connection.close()
    return opps

def search_opportunities(term, sort_by="o.name", order="ASC"):
    connection = get_connection()
    opps = []
    if connection:
        try:
            cursor = connection.cursor()
            query = f"""
            SELECT o.id, o.name, o.status, o.priority, o.estimated_value, o.proposal_deadline, o.expected_close_date, c.full_name, comp.name, u.username
            FROM opportunities o
            LEFT JOIN contacts c ON o.contact_id = c.id
            LEFT JOIN companies comp ON o.company_id = comp.id
            LEFT JOIN users u ON o.assigned_to = u.id
            WHERE o.name LIKE ? OR c.full_name LIKE ? OR comp.name LIKE ? OR o.status LIKE ?
            ORDER BY {sort_by} {order}
            """
            like_term = f"%{term}%"
            cursor.execute(query, (like_term, like_term, like_term, like_term))
            opps = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching opportunities: {e}")
        finally:
            connection.close()
    return opps

def delete_opportunity(opp_id):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM opportunities WHERE id = ?", (opp_id,))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting opportunity: {e}")
            return False
        finally:
            connection.close()
    return False