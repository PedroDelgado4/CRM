import customtkinter as ctk
import os
import webbrowser
from PIL import Image 
from core.contacts import add_contact, get_all_contacts, delete_contact, get_contacts_by_filter
from core.companies import get_all_companies 
from gui.client_details import ClientDetailsWindow 
from core.auth import get_all_users

class ContactView(ctk.CTkFrame): 
    def __init__(self, master, user_data):
        super().__init__(master, fg_color="transparent")
        self.user_data = user_data
        self.all_users = get_all_users()
        
        # COLORES
        self.color_green = "#2E8D1B"
        self.color_silver = "#D9D9D9"
        self.color_header = "#3F3F3F"
        self.color_brick = "#A52A2A"

        # ORDENACIÓN
        self.current_sort = "c.full_name"
        self.sort_order = "ASC"
        self.header_buttons = {}

        self.load_images()

        # BARRA DE HERRAMIENTAS SUPERIOR
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=10, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(self.toolbar, placeholder_text="🔍 Search contacts...", 
                                        width=300, border_color=self.color_green)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_list())

        self.add_btn = ctk.CTkButton(self.toolbar, text="+ New Contact", width=120, 
                                    fg_color=self.color_green, hover_color="#246B15",
                                    command=self.open_add_contact_window)
        self.add_btn.pack(side="right", padx=5)

        # CONFIGURACIÓN DE COLUMNAS
        self.col_widths = [40, 160, 140, 180, 120, 120, 120, 100]
        self.headers_info = [
            ("", "c.is_vip"), 
            ("NAME", "c.full_name"), 
            ("COMPANY", "comp.name"), 
            ("EMAIL", "c.email"), 
            ("PHONE", "c.phone"), 
            ("POSITION", "c.position"), 
            ("LINKEDIN", "c.linkedin"), 
            ("ACTIONS", None)
        ]

        # CABECERA
        self.header_frame = ctk.CTkFrame(self, height=35, corner_radius=0, fg_color=self.color_header)
        self.header_frame.pack(fill="x", padx=10)

        for i, (text, sort_key) in enumerate(self.headers_info):
            if sort_key:
                # Botón de ordenar
                btn = ctk.CTkButton(self.header_frame, text=text, fg_color="transparent", 
                                   text_color=self.color_silver, font=ctk.CTkFont(size=11, weight="bold"),
                                   width=self.col_widths[i], anchor="center", corner_radius=0,
                                   hover_color="#4F4F4F", command=lambda k=sort_key: self.set_sort(k))
                btn.grid(row=0, column=i, padx=5, pady=5)
                self.header_buttons[sort_key] = btn 
            else:
                lbl = ctk.CTkLabel(self.header_frame, text=text, text_color=self.color_silver, 
                                   font=ctk.CTkFont(size=11, weight="bold"), width=self.col_widths[i], anchor="center")
                lbl.grid(row=0, column=i, padx=5, pady=5)

        # LISTA SCROLLABLE
        self.list_frame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.list_frame.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        self.update_header_arrows()
        self.refresh_list()

    def set_sort(self, key):
        if self.current_sort == key:
            self.sort_order = "DESC" if self.sort_order == "ASC" else "ASC"
        else:
            self.current_sort = key
            self.sort_order = "ASC"
        
        self.update_header_arrows()
        self.refresh_list()

    def update_header_arrows(self):
        for key, btn in self.header_buttons.items():
            original_name = next(h[0] for h in self.headers_info if h[1] == key)
            if key == self.current_sort:
                arrow = " ▲" if self.sort_order == "ASC" else " ▼"
                # Evitar poner flecha en la columna vip
                if key == "c.is_vip":
                    btn.configure(text=original_name) 
                else:
                    btn.configure(text=f"{original_name}{arrow}")
            else:
                btn.configure(text=original_name)

    def open_link(self, url):
        if url and str(url) not in ["None", "", "-", "N/A"]:
            if not url.startswith("http"): url = "https://" + url
            webbrowser.open(url)

    def load_images(self):
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        def get_img(name):
            path = os.path.join(base_path, name)
            if os.path.exists(path): return ctk.CTkImage(Image.open(path), size=(16, 16))
            return None
        self.img_edit = get_img("edit.png")
        self.img_delete = get_img("trash.png")
        self.img_view = get_img("eye.png")
        self.img_star = get_img("star.png")

    def refresh_list(self, filter_mode="all"):
        for widget in self.list_frame.winfo_children(): widget.destroy()
        
        search_term = self.search_entry.get()
        # Llamada modificada para incluir ordenación
        contacts = get_contacts_by_filter(search_term=search_term, sort_by=self.current_sort, order=self.sort_order)

        for c in contacts:
            row = ctk.CTkFrame(self.list_frame, height=40, corner_radius=0, fg_color="transparent")
            row.pack(fill="x", pady=1)
            
            # Col 0: VIP
            vip_icon = self.img_star if c[3] == 1 else None
            ctk.CTkLabel(row, text="", image=vip_icon, width=self.col_widths[0]).grid(row=0, column=0, padx=5)

            # Col 1: Nombre
            ctk.CTkLabel(row, text=c[1], width=self.col_widths[1], anchor="center", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5)

            # Col 2: Empresa
            ctk.CTkLabel(row, text=c[2] or "-", width=self.col_widths[2], anchor="center", 
                         text_color=self.color_green).grid(row=0, column=2, padx=5)

            # Col 3: Email 
            em_txt = f"{c[4]}" if c[4] else "-"
            em_lbl = ctk.CTkLabel(row, text=em_txt, width=self.col_widths[3], anchor="center", 
                                  text_color="#5dade2" if c[4] else "gray", cursor="hand2" if c[4] else "")
            em_lbl.grid(row=0, column=3, padx=5)
            if c[4]: em_lbl.bind("<Button-1>", lambda e, mail=c[4]: self.open_link(f"mailto:{mail}"))

            # Col 4: Tlf
            ctk.CTkLabel(row, text=c[5] or "-", width=self.col_widths[4], anchor="center").grid(row=0, column=4, padx=5)

            # Col 5: Posicion
            ctk.CTkLabel(row, text=c[6] or "-", width=self.col_widths[5], anchor="center").grid(row=0, column=5, padx=5)

            # Col 6: Linkedin
            li_txt = "LinkedIn" if c[7] else "--------"
            li_lbl = ctk.CTkLabel(row, text=li_txt, width=self.col_widths[6], anchor="center", 
                                 text_color="#5dade2" if c[7] else "gray", cursor="hand2" if c[7] else "")
            li_lbl.grid(row=0, column=6, padx=5)
            if c[7]: li_lbl.bind("<Button-1>", lambda e, u=c[7]: self.open_link(u))

            # Col 7: Acciones
            actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[7])
            actions.grid(row=0, column=7, padx=5)
            
            ctk.CTkButton(actions, text="", image=self.img_view, width=25, height=25, fg_color="gray30",
                          command=lambda d=c: self.open_details(d)).pack(side="left", padx=2)
            ctk.CTkButton(actions, text="", image=self.img_delete, width=25, height=25, fg_color=self.color_brick,
                          command=lambda c_id=c[0]: self.remove_contact(c_id)).pack(side="left", padx=2)

            # Liinea divisoria
            ctk.CTkFrame(self.list_frame, height=1, fg_color="#2A2A2A").pack(fill="x", padx=10)

    def open_add_contact_window(self):
        if not hasattr(self, "add_win") or not self.add_win.winfo_exists():
            from gui.contact_popup import AddContactWindow
            self.add_win = AddContactWindow(self)
        self.add_win.focus()

    def open_details(self, contact_data): 
        details_win = ClientDetailsWindow(self, contact_data, self.all_users)
        details_win.attributes("-topmost", True)

    def remove_contact(self, contact_id): 
        if delete_contact(contact_id): self.refresh_list()