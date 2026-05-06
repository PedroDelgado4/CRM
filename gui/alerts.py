import customtkinter as ctk

def show_alert(parent, title, message, is_error=True):
    alert = ctk.CTkToplevel(parent)
    alert.title(title)
    alert.geometry("350x180")
    alert.attributes("-topmost", True)
    alert.grab_set() # Obliga al usuario a interactuar con la alerta
    

    color = "#A52A2A" if is_error else "#2E8D1B"
    hover_c = "#7A1F1F" if is_error else "#246B15"
    
    # Título
    ctk.CTkLabel(alert, text=title, font=ctk.CTkFont(weight="bold", size=18), text_color=color).pack(pady=(20, 10))
    
    # Mensaje (wraplength hace que el texto baje de línea si es muy largo)
    ctk.CTkLabel(alert, text=message, wraplength=300).pack(pady=(0, 20))
    
    # Boton ok
    ctk.CTkButton(alert, text="OK", width=120, fg_color=color, hover_color=hover_c, 
                 command=alert.destroy).pack()

    # Centrar la alerta en medio de la ventana padre
    alert.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (alert.winfo_width() // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (alert.winfo_height() // 2)
    alert.geometry(f"+{x}+{y}")