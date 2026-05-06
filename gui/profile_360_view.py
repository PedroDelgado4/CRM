import customtkinter as ctk
import os
from PIL import Image
from core.profile_360 import (get_company_details, get_company_contacts, 
                              get_company_opportunities, get_company_interactions, 
                              get_company_products, link_product_to_company, unlink_product_from_company)
from core.products import get_all_products
from gui.alerts import show_alert
import webbrowser

class Profile360View(ctk.CTkFrame):
    def __init__(self, master, company_id, go_back_callback):
        super().__init__(master, fg_color="transparent")
        self.company_id = company_id
        self.go_back_callback = go_back_callback
        
        self.color_green = "#2E8D1B"
        self.color_header = "#3F3F3F"
        self.color_brick = "#A52A2A"
        
        self.load_images()
        self.build_header()
        self.build_tabs()
        self.load_data()

    def load_images(self):
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        def get_img(name):
            path = os.path.join(base_path, name)
            if os.path.exists(path): return ctk.CTkImage(Image.open(path), size=(16, 16))
            return None
        self.img_delete = get_img("trash.png")

    def build_header(self):
        # Contenedor superior para datos de empresa y botón volver
        self.header_frame = ctk.CTkFrame(self, fg_color="#2A2A2A", corner_radius=10)
        self.header_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Botón Volver
        ctk.CTkButton(self.header_frame, text="← Back to Accounts", width=120, 
                      fg_color="transparent", border_width=1, border_color=self.color_green, 
                      hover_color="#3F3F3F", command=self.go_back_callback).pack(side="left", padx=15, pady=15)
        
        # Textos de la cabecera
        self.lbl_name = ctk.CTkLabel(self.header_frame, text="Company Name", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.color_green)
        self.lbl_name.pack(side="left", padx=(20, 10))
        
        # Industria/Tamaño
        self.lbl_industry_size = ctk.CTkLabel(self.header_frame, text="Industry | Size | ", text_color="#D9D9D9")
        self.lbl_industry_size.pack(side="left")

        # Website
        self.lbl_website = ctk.CTkLabel(self.header_frame, text="Website", text_color="#5dade2", cursor="hand2")
        self.lbl_website.pack(side="left")

    def build_tabs(self):
        self.tabview = ctk.CTkTabview(self, fg_color="transparent", segmented_button_selected_color=self.color_green, segmented_button_selected_hover_color="#246B15", text_color="#000000")
        self.tabview.pack(fill="both", expand=True, padx=10)
        
        self.tab_contacts = self.tabview.add("Contacts")
        self.tab_opps = self.tabview.add("Opportunities")
        self.tab_interactions = self.tabview.add("Interactions")
        self.tab_products = self.tabview.add("Active Products")

        # Preparar contenedores scrollables para cada pestaña
        self.scroll_contacts = ctk.CTkScrollableFrame(self.tab_contacts, fg_color="transparent")
        self.scroll_contacts.pack(fill="both", expand=True)
        
        self.scroll_opps = ctk.CTkScrollableFrame(self.tab_opps, fg_color="transparent")
        self.scroll_opps.pack(fill="both", expand=True)
        
        self.scroll_ints = ctk.CTkScrollableFrame(self.tab_interactions, fg_color="transparent")
        self.scroll_ints.pack(fill="both", expand=True)
        
        # En productos añadimos un botón superior para vincular nuevos
        self.prod_toolbar = ctk.CTkFrame(self.tab_products, fg_color="transparent")
        self.prod_toolbar.pack(fill="x", pady=(0, 5))
        ctk.CTkButton(self.prod_toolbar, text="+ Link Product", fg_color=self.color_green, hover_color="#246B15", command=self.open_link_product_popup).pack(side="right")
        
        self.scroll_prods = ctk.CTkScrollableFrame(self.tab_products, fg_color="transparent")
        self.scroll_prods.pack(fill="both", expand=True)

    def load_data(self):
        # 1. Cargar datos de la empresa
        details = get_company_details(self.company_id)
        if details:
            self.lbl_name.configure(text=details[1])
            
            ind_size_str = f"{details[2] or 'No Industry'} | {details[3] or 'No Size'} | "
            self.lbl_industry_size.configure(text=ind_size_str)
            
            website = details[4]
            if website:
                self.lbl_website.configure(text=website, text_color="#5dade2", cursor="hand2")
                # Le "enganchamos" el evento de clic izquierdo (<Button-1>)
                self.lbl_website.bind("<Button-1>", lambda e, url=website: self.open_link(url))
            else:
                self.lbl_website.configure(text="No Web", text_color="#D9D9D9", cursor="")
                self.lbl_website.unbind("<Button-1>") # Quitamos el evento si no hay web

        # 2. Cargar Contactos (id, full_name, email, phone, position)
        for w in self.scroll_contacts.winfo_children(): w.destroy()
        for c in get_company_contacts(self.company_id):
            row = ctk.CTkFrame(self.scroll_contacts, fg_color="#3F3F3F", corner_radius=5)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{c[1]}", font=ctk.CTkFont(weight="bold"), width=200, anchor="w", text_color="white").pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(row, text=c[4] or "No Position", width=150, anchor="w", text_color="white").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=c[2] or "No Email", width=200, anchor="w", text_color="white").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=c[3] or "No Phone", width=150, anchor="w", text_color="white").pack(side="left", padx=5)

        # 3. Cargar Oportunidades (id, name, status, value, close_date)
        for w in self.scroll_opps.winfo_children(): w.destroy()
        for o in get_company_opportunities(self.company_id):
            row = ctk.CTkFrame(self.scroll_opps, fg_color="#3F3F3F", corner_radius=5)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{o[1]}", font=ctk.CTkFont(weight="bold"), width=200, anchor="w", text_color=self.color_green).pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(row, text=o[2].replace("_", " ").title(), width=150, anchor="w", text_color="white").pack(side="left", padx=5)
            val = f"{o[3]:,.2f} €" if o[3] is not None else "0.00 €"
            ctk.CTkLabel(row, text=val, width=150, anchor="w", text_color="white").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=o[4] or "No Date", width=150, anchor="w", text_color="white").pack(side="left", padx=5)

        # 4. Cargar Interacciones (id, date_time, type, note, status, contact_name)
        for w in self.scroll_ints.winfo_children(): w.destroy()
        for i in get_company_interactions(self.company_id):
            row = ctk.CTkFrame(self.scroll_ints, fg_color="#3F3F3F", corner_radius=5)
            row.pack(fill="x", pady=2)
            dt = i[1].split(".")[0] if i[1] else "-"
            ctk.CTkLabel(row, text=f"{dt}", font=ctk.CTkFont(weight="bold"), width=150, anchor="w", text_color="white").pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(row, text=i[2].title(), width=80, anchor="w", text_color="white").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"con {i[5]}", width=150, anchor="w", text_color="#04ff00", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            note = i[3][:40] + "..." if len(i[3]) > 40 else i[3]
            ctk.CTkLabel(row, text=note, width=250, anchor="w", text_color="white").pack(side="left", padx=5)

        self.refresh_products()

    def refresh_products(self):
        for w in self.scroll_prods.winfo_children(): w.destroy()
        for p in get_company_products(self.company_id):
            row = ctk.CTkFrame(self.scroll_prods, fg_color="#3F3F3F", corner_radius=5)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{p[1]}", font=ctk.CTkFont(weight="bold"), width=200, anchor="w", text_color="white").pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(row, text=p[2] or "No Category", width=150, anchor="w", text_color="white").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=p[3] or "No Billing Model", width=150, anchor="w", text_color="white").pack(side="left", padx=5)
            
            ctk.CTkButton(row, text="", image=self.img_delete, width=28, height=28, fg_color=self.color_brick, hover_color="#7A1F1F",
                          command=lambda pid=p[0]: self.remove_product(pid)).pack(side="right", padx=10)

    def remove_product(self, product_id):
        if unlink_product_from_company(self.company_id, product_id):
            self.refresh_products()

    def open_link_product_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Link Product")
        popup.geometry("350x200")
        popup.attributes("-topmost", True)
        popup.grab_set()

        ctk.CTkLabel(popup, text="Select Product to Link:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        
        # Cargar todos los productos disponibles
        all_prods = get_all_products(sort_by="name", order="ASC")
        prod_dict = {p[1]: p[0] for p in all_prods}
        
        if not prod_dict:
            ctk.CTkLabel(popup, text="No products available in database.", text_color=self.color_brick).pack()
            return

        prod_var = ctk.StringVar(value=list(prod_dict.keys())[0])
        ctk.CTkOptionMenu(popup, variable=prod_var, values=list(prod_dict.keys()), fg_color="#3F3F3F", button_color=self.color_green).pack(pady=10, fill="x", padx=20)

        def save_link():
            selected_id = prod_dict[prod_var.get()]
            if link_product_to_company(self.company_id, selected_id):
                self.refresh_products()
                popup.destroy()
            else:
                show_alert(popup, "Notice", "This product is already linked to the company.", is_error=True)

        ctk.CTkButton(popup, text="Link", fg_color=self.color_green, hover_color="#246B15", command=save_link).pack(pady=15)
    
    def open_link(self, url):
        if url and str(url) not in ["None", "", "-", "N/A"]:
            # Añadimos https:// si el usuario olvidó ponerlo para que el navegador no falle
            if not url.startswith("http"): url = "https://" + url
            webbrowser.open(url)