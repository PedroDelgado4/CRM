import customtkinter as ctk
from gui.client_view import ClientView
from gui.admin_view import AdminView
from gui.profile_view import ProfileView

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
        

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Barra superior
        self.top_bar = ctk.CTkFrame(self.main_container, height=50, corner_radius=0)
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # nombre usuaroi
        self.user_btn = ctk.CTkButton(self.top_bar, text=f"👤 {self.user_data[1]}", fg_color="transparent", text_color=("black", "white"), width=100, command=lambda: self.change_view("Profile"))
        self.user_btn.pack(side="right", padx=20)
        #self.user_label = ctk.CTkLabel(self.top_bar, text=f"Welcome, {self.user_data[1]}", font=ctk.CTkFont(weight="bold"))
        #self.user_label.pack(side="right", padx=20)

        # Boton administrador
        if self.user_data[2] == "admin":
            self.admin_btn = ctk.CTkButton(self.top_bar, text="⚙️ Admin Panel", width=100, fg_color="#1f6aa5",hover_color="#144870", border_width=1, command=lambda: self.change_view("Admin"))
            self.admin_btn.pack(side="right", padx=20)
        
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        
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
        elif view_name == "Admin":
            self.admin_view = AdminView(self.content_frame)
            self.admin_view.pack(fill="both", expand=True)
        elif view_name == "Profile":
            self.profile_view = ProfileView(self.content_frame, self.user_data).pack(fill="both", expand=True)
        else:
            title = ctk.CTkLabel(self.content_frame, text=f"Viewing {view_name}", font=ctk.CTkFont(size=24))
            title.pack(pady=20)

        self.update_idletasks()

    def show_dashboard_stats(self):
        # mostrar un resumen rápido en el panl central
        info_text = f"Welcome back, {self.user_data[1]}!\nRole: {self.user_data[2]}"
        label = ctk.CTkLabel(self.content_frame, text=info_text)
        label.pack(pady=10)


