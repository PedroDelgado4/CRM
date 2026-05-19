import sqlite3
from core.database import get_connection

def add_opportunity(name, status, priority, estimated_value, proposal_deadline, expected_close_date, contact_id, company_id, assigned_to):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO opportunities 
            (name, status, priority, estimated_value, proposal_deadline, expected_close_date, contact_id, company_id, assigned_to) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (name, status, priority, estimated_value, proposal_deadline, expected_close_date, contact_id, company_id, assigned_to))
            connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding opportunity: {e}")
            return None
        finally:
            connection.close()
    return None

def get_all_opportunities(sort_by="o.name", order="ASC", status_filter=None):
    from core.database import get_connection
    connection = get_connection()
    opps = []
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT o.id, o.name, o.status, o.priority, o.estimated_value, 
               o.proposal_deadline, o.expected_close_date, 
               c.full_name, comp.name, u.username
        FROM opportunities o
        LEFT JOIN contacts c ON o.contact_id = c.id
        LEFT JOIN companies comp ON o.company_id = comp.id
        LEFT JOIN users u ON o.assigned_to = u.id
        """
        params = []
        
        # Inyectamos el filtro si existe y no es "All"
        if status_filter and status_filter != "All":
            query += " WHERE o.status = ?"
            params.append(status_filter)
            
        query += f" ORDER BY {sort_by} {order}"
        cursor.execute(query, tuple(params))
        opps = cursor.fetchall()
        connection.close()
    return opps

def get_all_opportunities(sort_by="o.name", order="ASC", status_filter=None):
    from core.database import get_connection
    connection = get_connection()
    opps = []
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT o.id, o.name, o.status, o.priority, o.estimated_value, 
               o.proposal_deadline, o.expected_close_date, 
               c.full_name, comp.name, u.username, o.last_contact 
        FROM opportunities o
        LEFT JOIN contacts c ON o.contact_id = c.id
        LEFT JOIN companies comp ON o.company_id = comp.id
        LEFT JOIN users u ON o.assigned_to = u.id
        """
        params = []
        if status_filter and status_filter != "All":
            query += " WHERE o.status = ?"
            params.append(status_filter)
            
        query += f" ORDER BY {sort_by} {order}"
        cursor.execute(query, tuple(params))
        opps = cursor.fetchall()
        connection.close()
    return opps

def search_opportunities(term, sort_by="o.name", order="ASC", status_filter=None):
    from core.database import get_connection
    connection = get_connection()
    opps = []
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT o.id, o.name, o.status, o.priority, o.estimated_value, 
               o.proposal_deadline, o.expected_close_date, 
               c.full_name, comp.name, u.username, o.last_contact
        FROM opportunities o
        LEFT JOIN contacts c ON o.contact_id = c.id
        LEFT JOIN companies comp ON o.company_id = comp.id
        LEFT JOIN users u ON o.assigned_to = u.id
        WHERE (o.name LIKE ? OR comp.name LIKE ? OR c.full_name LIKE ?)
        """
        like_term = f"%{term}%"
        params = [like_term, like_term, like_term]

        if status_filter and status_filter != "All":
            query += " AND o.status = ?"
            params.append(status_filter)
            
        query += f" ORDER BY {sort_by} {order}"
        cursor.execute(query, tuple(params))
        opps = cursor.fetchall()
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

def get_opportunity_by_id(opp_id):
    connection = get_connection()
    opp = None
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        opp = cursor.fetchone()
        connection.close()
    return opp

def update_opportunity(opp_id, name, status, priority, estimated_value, proposal_deadline, expected_close_date, contact_id, company_id, assigned_to):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            UPDATE opportunities 
            SET name=?, status=?, priority=?, estimated_value=?, proposal_deadline=?, expected_close_date=?, contact_id=?, company_id=?, assigned_to=?
            WHERE id=?
            """
            cursor.execute(query, (name, status, priority, estimated_value, proposal_deadline, expected_close_date, contact_id, company_id, assigned_to, opp_id))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating opportunity: {e}")
            return False
        finally:
            connection.close()
    return False

def link_product_to_opportunity(opp_id, product_id, quantity=1, price=0.0):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT OR REPLACE INTO opportunity_products (opportunity_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (opp_id, product_id, quantity, price))
            connection.commit()
            return True
        finally:
            connection.close()
    return False

def unlink_all_products_from_opportunity(opp_id):
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM opportunity_products WHERE opportunity_id = ?", (opp_id,))
        connection.commit()
        connection.close()

def get_opportunity_products(opp_id):
    connection = get_connection()
    products = []
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT p.id, p.name, op.quantity, op.unit_price 
        FROM products p
        JOIN opportunity_products op ON p.id = op.product_id
        WHERE op.opportunity_id = ?
        """
        cursor.execute(query, (opp_id,))
        products = cursor.fetchall()
        connection.close()
    return products

def update_last_contact_date(opportunity_id, date_str):
    from core.database import get_connection
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # Asumiendo que la columna en tu BD se llama 'last_contact'
            cursor.execute("UPDATE opportunities SET last_contact = ? WHERE id = ?", (date_str, opportunity_id))
            connection.commit()
            return True
        except Exception as e:
            print(f"Error updating last contact: {e}")
            return False
        finally:
            connection.close()
    return False