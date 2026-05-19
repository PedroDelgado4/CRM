import csv
from tkinter import filedialog, messagebox
from core.products import add_product


def export_table_to_csv(headers, data, filename_suggestion="export"):
    """
    Convierte cualquier lista de datos en un CSV descargable.
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile=f"{filename_suggestion}.csv"
    )
    
    if file_path:
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers) # Escribimos cabeceras
                writer.writerows(data)    # Escribimos los datos
            messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not export CSV: {e}")
            return False
    return False

def import_contacts_csv():
    from core.contacts import add_contact
    
    file_path = filedialog.askopenfilename(title="Select Contacts CSV File", filetypes=[("CSV files", "*.csv")])
    if not file_path: return False

    imported_count = 0
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [field.strip() for field in reader.fieldnames]
            
            for row in reader:
                # Normalización de Contactos
                name = (row.get("name") or row.get("full_name") or row.get("Name") or "").strip().title()
                email = (row.get("email") or row.get("Email") or "").strip().lower()
                phone = (row.get("phone") or row.get("Phone") or "").strip()
                position = (row.get("position") or row.get("Position") or "").strip().title()
                
                if name:
                    success = add_contact(name, None, 0, email, phone, position, "", None)
                    if success: imported_count += 1
                        
        messagebox.showinfo("Import Complete", f"Successfully imported {imported_count} contacts.")
        return True
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to import contacts:\n{e}")
        return False


def import_companies_csv():
    from core.companies import add_company
    
    file_path = filedialog.askopenfilename(title="Select Companies CSV", filetypes=[("CSV files", "*.csv")])
    if not file_path: return False

    count = 0
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [field.strip() for field in reader.fieldnames]
            
            for row in reader:
                # Normalización de Empresas
                name = (row.get("name") or row.get("company_name") or "").strip().title()
                industry = row.get("industry", "").strip().title()
                size = row.get("size", "").strip().title()
                website = row.get("website", "").strip().lower()
                linkedin = row.get("linkedin", "").strip().lower()
                address = row.get("address", "").strip()
                
                if name:
                    if add_company(name, industry, size, website, linkedin, address):
                        count += 1
                        
        messagebox.showinfo("Success", f"Imported {count} companies.")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Import failed: {e}")
        return False


def import_products_csv():
    from core.products import add_product 
    
    file_path = filedialog.askopenfilename(title="Select Products CSV", filetypes=[("CSV files", "*.csv")])
    if not file_path: return False

    count = 0
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [field.strip() for field in reader.fieldnames]

            for row in reader:
                # Normalización de Productos
                name = row.get("name", "").strip().title()
                description = row.get("description", "").strip()
                category = row.get("category", "").strip().title()
                
                try:
                    price = float(row.get("price", 0))
                except ValueError:
                    price = 0.0
                    
                # forzamos mayúsculas o capitalización según la lógica de la db
                billing_model = row.get("billing_model", "Single Payment").strip().title()
                status = row.get("status", "ACTIVE").strip().title()
                product_url = row.get("product_url", "").strip().lower()

                if name:
                    if add_product(name, description, category, price, billing_model, status, product_url):
                        count += 1
                        
        messagebox.showinfo("Success", f"Imported {count} products.")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Import failed:\n{e}")
        return False