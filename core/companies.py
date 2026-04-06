import sqlite3
from core.database import get_connection

def add_company(name, industry, size, website, linkedin, address):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO companies (name, industry, size, website, linkedin, address) VALUES (?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (name, industry, size, website, linkedin, address))
            connection.commit()
            return True
        except sqlite3.Error: return False
        finally: connection.close()
    return False

def get_all_companies(sort_by="name", order="ASC"):
    connection = get_connection()
    companies = []
    if connection:
        try:
            cursor = connection.cursor()
            # Aseguramos el orden de las columnas: id, name, industry, size, website, linkedin, address
            query = f"SELECT id, name, industry, size, website, linkedin, address FROM companies ORDER BY {sort_by} {order}"
            cursor.execute(query)
            companies = cursor.fetchall()
        finally: connection.close()
    return companies

def search_companies(term, sort_by="name", order="ASC"):
    connection = get_connection()
    companies = []
    if connection:
        try:
            cursor = connection.cursor()
            query = f"""
            SELECT id, name, industry, size, website, linkedin, address 
            FROM companies 
            WHERE name LIKE ? OR industry LIKE ? 
            ORDER BY {sort_by} {order}
            """
            cursor.execute(query, (f"%{term}%", f"%{term}%"))
            companies = cursor.fetchall()
        finally: connection.close()
    return companies

def delete_company(company_id):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
            connection.commit()
            return True
        finally: connection.close()
    return False