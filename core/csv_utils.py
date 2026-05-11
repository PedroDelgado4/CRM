import csv
from tkinter import filedialog, messagebox

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