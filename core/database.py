import sqlite3
from sqlite3 import Error
import hashlib

def get_connection():
    connection = None
    try:
        connection = sqlite3.connect('crm_data.db')
        return connection
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def initialize_db():
    connection = get_connection()
    if connection:
        cursor = connection.cursor()

        # Tabla usuarios
        cursor.execute('''
        
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'employee'))
        )''') 

        # Tabl clientes
        cursor.execute('''
        
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            company TEXT,
            email TEXT,
            phone TEXT,
            status TEXT DEFAULT 'lead',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')  


        # Tabla de interacciones
        cursor.execute('''
        
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            note TEXT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )''') 

        # Tabla finanzas (ingresos y gastos)
        cursor.execute('''
        
        CREATE TABLE IF NOT EXISTS finances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_type TEXT CHECK(entry_type IN ('income', 'expense')),
            amount REAL NOT NULL,
            description TEXT,
            date DATE DEFAULT CURRENT_DATE
        )''')

        hashed_admin_pw = hashlib.sha256('admin123'.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, role) 
                VALUES ('admin', ?, 'admin')
            ''', (hashed_admin_pw,))
        except Error as e:
            print(f"Error creating default admin: {e}")
        
        connection.commit()
        connection.close()
        print("Database initialized succesfully")