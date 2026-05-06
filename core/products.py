import sqlite3;
from core.database import get_connection

def add_product(name, description, category, min_price, billing_model, status, product_url):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO products (name, description, category, min_price, billing_model, status, product_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (name, description, category, min_price, billing_model, status, product_url))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding product: {e}")
            return False
        finally:
            connection.close()
    return False

def get_all_products(sort_by="name", order="ASC"):
    connection = get_connection()
    products = []
    if connection:
        try:
            cursor = connection.cursor()
            query = f"""
            SELECT id, name, description, category, min_price, billing_model, status, product_url
            FROM products
            ORDER BY {sort_by} {order}
            """
            cursor.execute(query)
            products = cursor.fetchall()
        finally: connection.close()
    return products

def search_products(term, sort_by="name", order="ASC"):
    connection = get_connection()
    products = []
    if connection:
        try:
            cursor = connection.cursor()
            query = f"""
            SELECT id, name, description, category, min_price, billing_model, status, product_url
            FROM products
            WHERE name LIKE ? OR category LIKE ? OR billing_model LIKE ?
            ORDER BY {sort_by} {order}
            """
            like_term = f"%{term}%"
            cursor.execute(query, (like_term, like_term, like_term))
            products = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching products: {e}")
        finally: connection.close()
    return products

def delete_product(product_id):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting product: {e}")
            return False
        finally: connection.close()
    return False

def update_product(product_id, name, description, category, min_price, billing_model, status, product_url):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            UPDATE products 
            SET name=?, description=?, category=?, min_price=?, billing_model=?, status=?, product_url=?
            WHERE id=?
            """
            cursor.execute(query, (name, description, category, min_price, billing_model, status, product_url, product_id))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating product: {e}")
            return False
        finally:
            connection.close()
    return False

            


