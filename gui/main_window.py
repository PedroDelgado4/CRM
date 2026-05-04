import customtkinter as ctk
import os 
from PIL import Image 
from gui.contact_view import ContactView 
from gui.company_view import CompanyView 
from gui.admin_view import AdminView
from gui.profile_view import ProfileView
from core.contacts import get_today_reminders 

class MainWindow(ctk.CTkFrame):
    def __init__(self, master, user_data):
        super().__init__(master)
        self.user_data = user_data 
        self.load_icons() 

        # COLORES
        self.color_green = "#2E8D1B"
        self.color_silver = "#D9D9D9"

        # Dicc para gestion de botones de nav
        self.nav_buttons = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # BARRA DE NAVEGACIÓN SUPERIOR
        self.top_nav = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#3F3F3F") # MODIFICADO: Fondo gris oscuro
        self.top_nav.grid(row=0, column=0, sticky="ew")

        # Logo
        self.logo_label = ctk.CTkLabel(self.top_nav, text="CRM FDT", text_color=self.color_silver, font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_label.pack(side="left", padx=20)

        # Botones
        self.nav_buttons["Dashboard"] = self.create_nav_btn("Dashboard", self.icon_dashboard)
        self.nav_buttons["Companies"] = self.create_nav_btn("Companies", self.icon_company)
        self.nav_buttons["Contacts"] = self.create_nav_btn("Contacts", self.icon_contact)
        self.nav_buttons["Finances"] = self.create_nav_btn("Finances", self.icon_finance)
        self.nav_buttons["Products"] = self.create_nav_btn("Products", self.icon_product)

        # Usuario y notif
        self.user_btn = ctk.CTkButton(self.top_nav, text=f" {self.user_data[1]}", 
            image=self.icon_user, compound="left",
            fg_color="transparent", text_color=self.color_silver, 
            hover_color="#4F4F4F", width=100, command=lambda: self.change_view("Profile"))
        self.user_btn.pack(side="right", padx=10)

        self.update_bell()

        if self.user_data[2] == "admin":
            self.admin_btn = ctk.CTkButton(self.top_nav, text="Admin", 
                image=self.icon_admin, compound="left",
                width=80, fg_color=self.color_green, hover_color="#246B15", # MODIFICADO: Tu nuevo verde
                command=lambda: self.change_view("Admin"))
            self.admin_btn.pack(side="right", padx=10)
        
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.change_view("Dashboard")

    def create_nav_btn(self, name, icon):
        btn = ctk.CTkButton(self.top_nav, text=f" {name}", image=icon, 
                           compound="left", fg_color="transparent", 
                           text_color=self.color_silver, hover_color="#4F4F4F",
                           width=110, command=lambda n=name: self.change_view(n))
        btn.pack(side="left", padx=5, pady=10)
        return btn

    def load_icons(self):
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        def get_icon(name):
            path = os.path.join(base_path, name)
            if os.path.exists(path):
                img = Image.open(path)
                return ctk.CTkImage(light_image=img, dark_image=img, size=(18,18))
            return None
        self.icon_dashboard = get_icon("dashboard.png")
        self.icon_company = get_icon("company.png")
        self.icon_contact = get_icon("contact.png")
        self.icon_finance = get_icon("finance.png")
        self.icon_user = get_icon("user.png")
        self.icon_admin = get_icon("settings.png")
        self.icon_bell = get_icon("bell.png")
        self.icon_product = get_icon("package.png")


    def update_bell(self):
        reminders = get_today_reminders(self.user_data[0])
        count = len(reminders)
        
        if count > 0:
            bg_color = "#d4a017"; txt_color = "white"; hvr_color = "#b88a10"; bell_text = f" {count}"
        else:
            bg_color = "#333333"; txt_color = "gray"; hvr_color = "#444444"; bell_text = ""

        if not hasattr(self, "notif_btn"):
            self.notif_btn = ctk.CTkButton(
                self.top_nav, text=bell_text, image=self.icon_bell, # Cambiado top_bar a top_nav
                width=45, height=30, fg_color=bg_color, text_color=txt_color,
                hover_color=hvr_color, corner_radius=8, command=self.show_reminders_popup)
            self.notif_btn.pack(side="right", padx=10)
        else:
            self.notif_btn.configure(text=bell_text, fg_color=bg_color, text_color=txt_color, hover_color=hvr_color)

    def change_view(self, view_name):
        # iluminar boton seleccionado
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=self.color_green, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=self.color_silver)
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.update_bell()
        
        if view_name == "Dashboard": self.show_dashboard_stats()
        elif view_name == "Companies": 
            self.company_view = CompanyView(self.content_frame); self.company_view.pack(fill="both", expand=True)
        elif view_name == "Contacts": 
            self.contact_view = ContactView(self.content_frame, self.user_data); self.contact_view.pack(fill="both", expand=True)
        elif view_name == "Admin":
            self.admin_view = AdminView(self.content_frame); self.admin_view.pack(fill="both", expand=True)
        elif view_name == "Profile":
            self.profile_view = ProfileView(self.content_frame, self.user_data).pack(fill="both", expand=True)
        elif view_name == "Products":
            from gui.product_view import ProductView
            self.product_view = ProductView(self.content_frame)
            self.product_view.pack(fill="both", expand=True)
        else:
            title = ctk.CTkLabel(self.content_frame, text=f"Viewing {view_name}", font=ctk.CTkFont(size=24))
            title.pack(pady=20)
        self.update_idletasks()

    def show_dashboard_stats(self):
        label = ctk.CTkLabel(self.content_frame, text=f"Welcome back, {self.user_data[1]}!\nRole: {self.user_data[2]}")
        label.pack(pady=10)

    def show_reminders_popup(self):
        reminders = get_today_reminders(self.user_data[0])
        popup = ctk.CTkToplevel(self)
        popup.title("Reminders")
        popup.geometry("380x480")
        popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text="Today's Reminders", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        if not reminders:
            ctk.CTkLabel(popup, text="No reminders today.").pack(pady=20)
        else:
            scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=10, pady=10)
            for name, company, note in reminders:
                frame = ctk.CTkFrame(scroll); frame.pack(fill="x", pady=5, padx=10)
                ctk.CTkLabel(frame, text=f"{name} | {company}" if company else name, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 0))
                ctk.CTkLabel(frame, text=note, wraplength=280, justify="left").pack(anchor="w", padx=10, pady=(5, 5))