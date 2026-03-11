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