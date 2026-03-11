import customtkinter as ctk
from gui.client_view import ClientView

class MainWindow(ctk.CTkFrame):
    def __init__(self, master, user_data):
        super().__init__(master)
        self.user_data = user_data # guardar datos de usuario logeado

        # Cuadricula: 0 para menú (fija) y 1 para contenido (se expande)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # menu lateral
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="CRM FDT", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # Botones de navegacion
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=lambda: self.change_view("Dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_clients = ctk.CTkButton(self.sidebar_frame, text="Clients & Leads", command=lambda: self.change_view("Clients"))
        self.btn_clients.grid(row=2, column=0, padx=20, pady=10)

        self.btn_finances = ctk.CTkButton(self.sidebar_frame, text="Finances", command=lambda: self.change_view("Finances"))
        self.btn_finances.grid(row=3, column=0, padx=20, pady=10)

        # area de contenido principal
        self.content_frame = ctk.CTkFrame(self, corner_radius=10)
        self.content_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # por defecto se muestra dashboard al entrar
        self.change_view("Dashboard")

    def change_view(self, view_name):
        # limpiar el area de contenido y mostrar lo seleccionado
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if view_name == "Dashboard":
            self.show_dashboard_stats()
        elif view_name == "Clients":
            self.client_view = ClientView(self.content_frame)
            self.client_view.pack(fill="both", expand=True)
        else:
            title = ctk.CTkLabel(self.content_frame, text=f"Viewing {view_name}", font=ctk.CTkFont(size=24))
            title.pack(pady=20)

    def show_dashboard_stats(self):
        # mostrar un resumen rápido en el panl central
        info_text = f"Welcome back, {self.user_data[1]}!\nRole: {self.user_data[2]}"
        label = ctk.CTkLabel(self.content_frame, text=info_text)
        label.pack(pady=10)


