import sqlite3
import hashlib
from core.database import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        hashed_pw = hash_password(password)
        query = "SELECT id, username, role FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, hashed_pw))
        user_data = cursor.fetchone()
        connection.close()

        return user_data
    return None

def add_user(username, password, role):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            hashed_pw = hash_password(password)
            query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
            cursor.execute(query, (username, hashed_pw, role))
            connection.commit()
            print(f"User {username} added successfully.")
            return True

        except sqlite3.IntegrityError:
            print("Username already exists")
            return False
        finally:
            connection.close()
    return False

def get_all_users():
    connection = get_connection()
    users = []
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()
        connection.close()
    return users

def delete_user(user_id):
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        connection.commit()
        connection.close()
        return True
    return False

def update_password(user_id, new_password):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            hashed_pw = hash_password(new_password)
            query = "UPDATE users SET password = ? WHERE id = ?"
            cursor.execute(query, (hashed_pw, user_id))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating password {e}")
            return False
        finally:
            connection.close()
    return False


            