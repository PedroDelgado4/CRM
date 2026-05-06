import sqlite3
from core.database import get_connection

def get_company_details(company_id):
    connection = get_connection()
    details = None
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        details = cursor.fetchone()
        connection.close()
    return details

def get_company_contacts(company_id):
    connection = get_connection()
    contacts = []
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, full_name, email, phone, position FROM contacts WHERE company_id = ?", (company_id,))
        contacts = cursor.fetchall()
        connection.close()
    return contacts

def get_company_opportunities(company_id):
    connection = get_connection()
    opps = []
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, status, estimated_value, expected_close_date FROM opportunities WHERE company_id = ?", (company_id,))
        opps = cursor.fetchall()
        connection.close()
    return opps

def get_company_interactions(company_id):
    connection = get_connection()
    interactions = []
    if connection:
        cursor = connection.cursor()
        # Buscamos interacciones de todos los contactos que pertenezcan a esta empresa
        query = """
        SELECT i.id, i.date_time, i.type, i.note, i.status, c.full_name 
        FROM interactions i
        JOIN contacts c ON i.contact_id = c.id
        WHERE c.company_id = ?
        ORDER BY i.date_time DESC
        """
        cursor.execute(query, (company_id,))
        interactions = cursor.fetchall()
        connection.close()
    return interactions

def get_company_products(company_id):
    connection = get_connection()
    products = []
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT p.id, p.name, p.category, p.billing_model, p.status 
        FROM products p
        JOIN company_products cp ON p.id = cp.product_id
        WHERE cp.company_id = ?
        """
        cursor.execute(query, (company_id,))
        products = cursor.fetchall()
        connection.close()
    return products

def link_product_to_company(company_id, product_id):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO company_products (company_id, product_id) VALUES (?, ?)", (company_id, product_id))
            connection.commit()
            return True
        except sqlite3.IntegrityError:
            # Significa que este producto ya estaba enlazado a esta empresa (evita duplicados)
            return False
        finally:
            connection.close()
    return False

def unlink_product_from_company(company_id, product_id):
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM company_products WHERE company_id = ? AND product_id = ?", (company_id, product_id))
        connection.commit()
        connection.close()
        return True
    return False