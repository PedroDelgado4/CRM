import customtkinter as ctk
import os 
from PIL import Image 
from gui.contact_view import ContactView 
from gui.company_view import CompanyView 
from gui.admin_view import AdminView
from gui.profile_view import ProfileView
from core.notifications import get_all_alerts
from gui.opportunity_view import OpportunityView
from gui.interaction_view import InteractionView
from gui.finance_view import FinanceView
from gui.dashboard_view import DashboardView

class MainWindow(ctk.CTkFrame):
    def __init__(self, master, user_data):
        super().__init__(master, fg_color="#050505") # Fondo Neon Night
        
        # FIJAMOS EL TAMAÑO MÍNIMO DE LA VENTANA PRINCIPAL
        self.master.minsize(1300, 800) 
        ctk.set_appearance_mode("Dark") # Forzamos modo oscuro por defecto
        
        self.user_data = user_data 
        self.load_icons() 

        # COLORES NEON NIGHT
        self.color_neon = "#DEFF9A"
        self.color_silver = "#888888" 
        self.color_surface = "#151515"

        self.nav_buttons = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # BARRA DE NAVEGACIÓN SUPERIOR
        self.top_nav = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#3A3A3A", border_width=1, border_color="#222")
        self.top_nav.grid(row=0, column=0, sticky="ew")

        # Logo
        self.logo_label = ctk.CTkLabel(self.top_nav, text="CRM FDT", text_color=self.color_neon, font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(side="left", padx=20)

        # Botones Nav
        self.nav_buttons["Dashboard"] = self.create_nav_btn("Dashboard", self.icon_dashboard)
        self.nav_buttons["Companies"] = self.create_nav_btn("Companies", self.icon_company)
        self.nav_buttons["Contacts"] = self.create_nav_btn("Contacts", self.icon_contact)
        self.nav_buttons["Finances"] = self.create_nav_btn("Finances", self.icon_finance)
        self.nav_buttons["Products"] = self.create_nav_btn("Products", self.icon_product)
        self.nav_buttons["Opportunities"] = self.create_nav_btn("Opportunities", self.icon_opportunity)
        self.nav_buttons["Interactions"] = self.create_nav_btn("Interactions", self.icon_interaction)

        # Usuario y notif
        self.user_btn = ctk.CTkButton(self.top_nav, text=f" {self.user_data[1]}", 
            image=self.icon_user, compound="left",
            fg_color="transparent", text_color="white", 
            hover_color="#2A2A2A", width=100, command=lambda: self.change_view("Profile"))
        self.user_btn.pack(side="right", padx=10)

        self.update_bell()

        if self.user_data[2] == "admin":
            self.admin_btn = ctk.CTkButton(self.top_nav, text="Admin", 
                image=self.icon_admin, compound="left",
                width=80, fg_color="transparent", border_width=1, border_color=self.color_neon, text_color=self.color_neon, hover_color="#2A2A2A",
                command=lambda: self.change_view("Admin"))
            self.admin_btn.pack(side="right", padx=10)
        
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.change_view("Dashboard")

    def create_nav_btn(self, name, icon):
        btn = ctk.CTkButton(self.top_nav, text=f" {name}", image=icon, 
                           compound="left", fg_color="transparent", 
                           text_color=self.color_silver, hover_color="#2A2A2A",
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
        self.icon_opportunity = get_icon("target.png")
        self.icon_interaction = get_icon("interaction.png")

    def update_bell(self):
        alerts = get_all_alerts(self.user_data[0])
        count = len(alerts)
        
        if count > 0:
            bg_color = "#F6FF00"; txt_color = "black"; hvr_color = "#bde072"; bell_text = f" {count}"
        else:
            bg_color = "transparent"; txt_color = self.color_silver; hvr_color = "#2A2A2A"; bell_text = ""

        if not hasattr(self, "notif_btn"):
            self.notif_btn = ctk.CTkButton(
                self.top_nav, text=bell_text, image=self.icon_bell, 
                width=45, height=30, fg_color=bg_color, text_color=txt_color,
                hover_color=hvr_color, corner_radius=8, command=self.show_notification_center)
            self.notif_btn.pack(side="right", padx=10)
        else:
            self.notif_btn.configure(text=bell_text, fg_color=bg_color, text_color=txt_color, hover_color=hvr_color)
            self.notif_btn.configure(command=self.show_notification_center)

    def show_notification_center(self):
        alerts = get_all_alerts(self.user_data[0])
        popup = ctk.CTkToplevel(self)
        popup.title("Notification Center")
        popup.geometry("450x600")
        popup.minsize(400, 500)
        popup.attributes("-topmost", True)
        
        popup.configure(fg_color="#050505")
        
        # Cabecera
        header_frame = ctk.CTkFrame(popup, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header_frame, text="NOTIFICATION CENTER", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.color_neon).pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Smart proactive alerts for your workflow.", text_color="#888888").pack(anchor="w")
        
        if not alerts:
            ctk.CTkLabel(popup, text="All caught up! No new alerts.", text_color="#888").pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        for alert in alerts:
            # Base con el color de la severidad (Actúa como borde exterior)
            card_base = ctk.CTkFrame(scroll, fg_color=alert["color"], corner_radius=6)
            card_base.pack(fill="x", pady=5, padx=10)
            
            # 2. Le pegamos encima la tarjeta gris oscura, pero desplazada 5px a la izquierda (padx=(5, 1))
            # Así conseguimos la franja lateral perfecta sin romper el alto dinámico.
            card = ctk.CTkFrame(card_base, fg_color="#151515", corner_radius=5)
            card.pack(fill="both", expand=True, padx=(5, 1), pady=1)
            
            # 3. Textos (El alto de estos textos definirá el alto de TODA la tarjeta)
            ctk.CTkLabel(card, text=alert["title"], font=ctk.CTkFont(size=14, weight="bold"), text_color=alert["color"]).pack(anchor="w", padx=15, pady=(10, 2))
            ctk.CTkLabel(card, text=alert["msg"], wraplength=320, justify="left", text_color="white").pack(anchor="w", padx=15, pady=(0, 10))

    # --- PARCHE PARA EL BUG DE COMBOBOX DE CUSTOMTKINTER ---
    def clean_dropdowns(self, widget):
        if hasattr(widget, "_dropdown_menu"):
            try: widget._dropdown_menu.destroy()
            except: pass
        for child in widget.winfo_children():
            self.clean_dropdowns(child)

    def change_view(self, view_name):
        # Iluminar boton seleccionado
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=self.color_neon, text_color="#2A2A2A", hover_color=self.color_neon)
            else:
                btn.configure(fg_color="transparent", text_color="white", hover_color="#2A2A2A")
        
        # Destruir menús desplegables de forma segura antes de borrar la vista
        self.clean_dropdowns(self.content_frame)

        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        self.update_bell()
        
        if view_name == "Dashboard":
            self.dash_view = DashboardView(self.content_frame, self.user_data); self.dash_view.pack(fill="both", expand=True)
        elif view_name == "Companies": 
            self.company_view = CompanyView(self.content_frame, self.user_data); self.company_view.pack(fill="both", expand=True)
        elif view_name == "Contacts": 
            self.contact_view = ContactView(self.content_frame, self.user_data); self.contact_view.pack(fill="both", expand=True)
        elif view_name == "Admin":
            self.admin_view = AdminView(self.content_frame); self.admin_view.pack(fill="both", expand=True)
        elif view_name == "Profile":
            self.profile_view = ProfileView(self.content_frame, self.user_data); self.profile_view.pack(fill="both", expand=True)
        elif view_name == "Products":
            from gui.product_view import ProductView
            self.product_view = ProductView(self.content_frame, self.user_data); self.product_view.pack(fill="both", expand=True)
        elif view_name == "Opportunities":
            self.opp_view = OpportunityView(self.content_frame, self.user_data); self.opp_view.pack(fill="both", expand=True)
        elif view_name == "Interactions":
            self.int_view = InteractionView(self.content_frame, self.user_data); self.int_view.pack(fill="both", expand=True)
        elif view_name == "Finances":
            self.finance_view = FinanceView(self.content_frame, self.user_data); self.finance_view.pack(fill="both", expand=True)    
        else:
            title = ctk.CTkLabel(self.content_frame, text=f"Viewing {view_name}", font=ctk.CTkFont(size=24))
            title.pack(pady=20)
        self.update_idletasks()

    def show_reminders_popup(self):
        reminders = get_all_alerts(self.user_data[0])
        popup = ctk.CTkToplevel(self)
        popup.title("Reminders")
        popup.geometry("400x500")
        popup.minsize(380, 480)
        popup.attributes("-topmost", True)
        
        popup.configure(fg_color="#050505")
        ctk.CTkLabel(popup, text="TODAY's REMINDERS", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.color_neon).pack(pady=20)
        
        if not reminders:
            ctk.CTkLabel(popup, text="No reminders today.", text_color="#888").pack(pady=20)
        else:
            scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=10, pady=10)
            for name, company, note in reminders:
                frame = ctk.CTkFrame(scroll, fg_color="#151515", border_width=1, border_color="#333")
                frame.pack(fill="x", pady=5, padx=10)
                ctk.CTkLabel(frame, text=f"{name} | {company}" if company else name, font=ctk.CTkFont(weight="bold"), text_color="white").pack(anchor="w", padx=10, pady=(10, 0))
                ctk.CTkLabel(frame, text=note, wraplength=280, justify="left", text_color="#aaa").pack(anchor="w", padx=10, pady=(5, 10))