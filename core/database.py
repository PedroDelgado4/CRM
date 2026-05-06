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

        # 1. TABLA USUARIOS
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'employee'))
        )''') 

        # 2. TABLA EMPRESAS (Accounts)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT,
            size TEXT,
            website TEXT,
            linkedin TEXT,
            address TEXT
        )''')

        # 3. TABLA CONTACTOS
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            company_id INTEGER, 
            is_vip INTEGER DEFAULT 0,
            email TEXT,
            phone TEXT,
            position TEXT,
            linkedin TEXT,
            assigned_to INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (assigned_to) REFERENCES users (id)
        )''')

        # 4. TABLA PRODUCTOS/SERVICIOS
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            min_price REAL,
            billing_model TEXT,
            status TEXT,
            product_url TEXT
        )''')

        # 5. TABLA OPORTUNIDADES
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT CHECK(status IN ('qualification', 'proposal', 'evaluation', 'negotiation', 'closed_won', 'closed_lost')),
            priority TEXT CHECK(priority IN ('very_high', 'medium', 'low', 'very_low')),
            assigned_to INTEGER,
            estimated_value REAL,
            proposal_deadline DATE,
            expected_close_date DATE,
            contact_id INTEGER,
            company_id INTEGER,
            FOREIGN KEY (assigned_to) REFERENCES users (id),
            FOREIGN KEY (contact_id) REFERENCES contacts (id),
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )''')

        # 6. TABLA INTERACCIONES
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            opportunity_id INTEGER,
            type TEXT, 
            note TEXT,
            date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            reminder_date DATE,
            FOREIGN KEY (contact_id) REFERENCES contacts (id),
            FOREIGN KEY (opportunity_id) REFERENCES opportunities (id)
        )''')

        # 7. TABLA INTERMEDIA: Productos en Interacciones
        # Esto permite ligar varios productos a una sola reunion/nota
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS interaction_products (
            interaction_id INTEGER,
            product_id INTEGER,
            FOREIGN KEY (interaction_id) REFERENCES interactions (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )''')

        # 8. TABLA INTERMEDIA: Productos en Oportunidades
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunity_products (
            opportunity_id INTEGER,
            product_id INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )''')

        # 8.5 TABLA INTERMEDIA: Productos vinculados al Cliente (Cartera)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_products (
            company_id INTEGER,
            product_id INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            PRIMARY KEY (company_id, product_id)
        )''')

        # 9. TABLA FINANZAS
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS finances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_type TEXT CHECK(entry_type IN ('income', 'expense')),
            amount REAL NOT NULL,
            description TEXT,
            date DATE DEFAULT CURRENT_DATE
        )''')

        # Admin por defect
        hashed_admin_pw = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES ("admin", ?, "admin")', (hashed_admin_pw,))
        
        connection.commit()
        connection.close()
        print("Database initialized successfully with Pro Relational Model")