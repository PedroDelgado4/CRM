import sqlite3
from core.database import get_connection

def add_client(full_name, company, email, phone, status="lead"):
    # guardar un nuevo cliente o lead en la db
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO clients (full_name, company, email, phone, status)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (full_name, company, email, phone, status))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding client: {e}")
            return False
        finally:
            connection.close()
    return False

def get_all_clients():
    # Lista de todos los clientes y leads
    connection = get_connection()
    clients = []
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, full_name, company, status FROM clients")
            clients = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching clients: {e}")
        finally:
            connection.close()
            
    return clients

def search_clients(term):
    # busqueda de clientes por nombre o empresa
    connection = get_connection()
    clients = []
    if connection:
        try:
            cursor = connection.cursor()
            query = """ SELECT id, full_name, company, status FROM clients WHERE full_name LIKE ? OR company LIKE ? """
            filter_item = f"%{term}%"
            cursor.execute(query, (filter_item, filter_item))
            clients = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching clients: {e}")
        finally:
            connection.close()
    return clients

def delete_client(client_id):
    # eliminar cliente
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting client: {e}")
            return False
        finally:
            connection.close()
    return False    
            