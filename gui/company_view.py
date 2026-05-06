import customtkinter as ctk
import os
import webbrowser
from PIL import Image
from core.companies import get_all_companies, search_companies, delete_company
from gui.company_popup import AddCompanyWindow

class CompanyView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Colores
        self.color_green = "#2E8D1B"
        self.color_silver = "#D9D9D9"
        self.color_header = "#3F3F3F"
        self.color_brick = "#A52A2A"

        self.current_sort = "name"
        self.sort_order = "ASC"

        self.header_buttons = {}

        # ANCHOS 
        self.col_widths = [200, 150, 80, 160, 160, 220, 100]
        self.headers_info = [
            ("NAME", "name"), ("INDUSTRY", "industry"), ("SIZE", "size"), 
            ("WEBSITE", "website"), ("LINKEDIN", "linkedin"), ("ADDRESS", "address"), 
            ("ACTIONS", None)
        ]

        self.load_images()

        # Toolbar
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=10, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(self.toolbar, placeholder_text="🔍 Search name or industry...", 
                                        width=300, border_color=self.color_green)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_list())

        self.add_btn = ctk.CTkButton(self.toolbar, text="+ New Account", width=120, 
                                    fg_color=self.color_green, command= self.open_add_company_window,
                                    hover_color="#246B15")
        self.add_btn.pack(side="right", padx=5)

        # CABECERA 
        self.header_frame = ctk.CTkFrame(self, height=35, corner_radius=0, fg_color=self.color_header)
        self.header_frame.pack(fill="x", padx=10)

        for i, (text, sort_key) in enumerate(self.headers_info):
            if sort_key:
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

        # LISTA
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
                arrow= " ▲" if self.sort_order == "ASC" else " ▼"
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
        self.img_delete = get_img("trash.png")
        self.img_view = get_img("eye.png") 

    def refresh_list(self):
        for widget in self.list_frame.winfo_children(): widget.destroy()
        
        term = self.search_entry.get()
        companies = search_companies(term, self.current_sort, self.sort_order) if term else get_all_companies(self.current_sort, self.sort_order)

        for comp in companies:
            row = ctk.CTkFrame(self.list_frame, height=40, corner_radius=0, fg_color="transparent")
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=comp[1], width=self.col_widths[0], anchor="center", 
                         text_color=self.color_green, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5)

            ctk.CTkLabel(row, text=comp[2] or "-", width=self.col_widths[1], anchor="center").grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row, text=comp[3] or "-", width=self.col_widths[2], anchor="center").grid(row=0, column=2, padx=5)

            web_txt = f"{comp[4]}" if comp[4] else "-"
            web_lbl = ctk.CTkLabel(row, text=web_txt, width=self.col_widths[3], anchor="center", 
                                  text_color="#5dade2" if comp[4] else "gray", cursor="hand2" if comp[4] else "")
            web_lbl.grid(row=0, column=3, padx=5)
            if comp[4]: web_lbl.bind("<Button-1>", lambda e, u=comp[4]: self.open_link(u))

            li_txt = "LinkedIn" if comp[5] else "-"
            li_lbl = ctk.CTkLabel(row, text=li_txt, width=self.col_widths[4], anchor="center", 
                                 text_color="#5dade2" if comp[5] else "gray", cursor="hand2" if comp[5] else "")
            li_lbl.grid(row=0, column=4, padx=5)
            if comp[5]: li_lbl.bind("<Button-1>", lambda e, u=comp[5]: self.open_link(u))

            ctk.CTkLabel(row, text=comp[6] or "-", width=self.col_widths[5], anchor="center").grid(row=0, column=5, padx=5)

            # Col 6: Acciones 
            actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[6])
            actions.grid(row=0, column=6, padx=5)
            
            # Sub-contenedor para centrar los botones
            btn_container = ctk.CTkFrame(actions, fg_color="transparent")
            btn_container.pack(expand=True)
            
            # Botón Ojo (Ver Ficha)
            ctk.CTkButton(btn_container, text="👁️" if not self.img_view else "", image=self.img_view, 
                          width=28, height=28, fg_color="#3498db", hover_color="#21618c",
                          command=lambda c_id=comp[0]: self.open_profile(c_id)).pack(side="left", padx=(0, 5))

            # Botón Papelera
            ctk.CTkButton(btn_container, text="🗑️" if not self.img_delete else "", image=self.img_delete, 
                          width=28, height=28, fg_color=self.color_brick, hover_color="#7A1F1F",
                          command=lambda c_id=comp[0]: self.remove_company(c_id)).pack(side="left")

            # Línea divisoria
            ctk.CTkFrame(self.list_frame, height=1, fg_color="#2A2A2A").pack(fill="x", padx=10)

    def open_add_company_window(self):
        if not hasattr(self, "add_win") or not self.add_win.winfo_exists():
            self.add_win = AddCompanyWindow(self)
        else:
            self.add_win.focus()

    def remove_company(self, company_id):
        if delete_company(company_id): self.refresh_list()

    # --- NUEVOS MÉTODOS PARA EL PERFIL 360 ---
    def open_profile(self, company_id):
        # 1. Ocultar la lista de empresas
        self.toolbar.pack_forget()
        self.header_frame.pack_forget()
        self.list_frame.pack_forget()

        # 2. Cargar y mostrar la Ficha 360
        from gui.profile_360_view import Profile360View
        self.profile_view = Profile360View(self, company_id, self.close_profile)
        self.profile_view.pack(fill="both", expand=True)

    def close_profile(self):
        # 1. Destruir la Ficha 360
        if hasattr(self, "profile_view"):
            self.profile_view.destroy()

        # 2. Volver a mostrar la lista de empresas
        self.toolbar.pack(fill="x", padx=10, pady=(0, 10))
        self.header_frame.pack(fill="x", padx=10)
        self.list_frame.pack(pady=(0, 10), padx=10, fill="both", expand=True)
        self.refresh_list()