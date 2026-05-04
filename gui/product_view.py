import customtkinter as ctk
import os
import webbrowser
from PIL import Image
from core.products import get_all_products, search_products, delete_product
from gui.product_popup import AddProductWindow

class ProductView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.color_green = "#2E8D1B"
        self.color_silver = "#D9D9D9"
        self.color_header = "#3F3F3F"
        self.color_brick = "#A52A2A"

        self.current_sort = "name"
        self.sort_order = "ASC"
        self.header_buttons = {}

        self.load_images()

        # config de columnsa
        self.col_widths = [180, 220, 100, 100, 140, 100, 100, 80]
        self.headers_info = [
            ("NAME", "name"), ("DESCRIPTION", "description"), ("CATEGORY", "category"), 
            ("MIN PRICE", "min_price"), ("BILLING MODEL", "billing_model"), ("STATUS", "status"), 
            ("PRODUCT URL", "product_url"), ("ACTIONS", None)
        ]

        # barar de herramientas
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=10, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(self.toolbar, placeholder_text="🔍 Search products...", 
                                        width=300, border_color=self.color_green)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_list())

        self.add_btn = ctk.CTkButton(self.toolbar, text="+ New Product", width=120, 
                                    fg_color=self.color_green, hover_color="#246B15",
                                    command=self.open_add_product_window)
        self.add_btn.pack(side="right", padx=5)

        # cabecera
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
                
        # lista scrollable
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

    def refresh_list(self):
        for widget in self.list_frame.winfo_children(): widget.destroy()

        term = self.search_entry.get()
        # id(0), name(1), description(2), category(3), min_price(4), billing_model(5), status(6), product_url(7)
        products = search_products(term, self.current_sort, self.sort_order) if term else get_all_products(self.current_sort, self.sort_order)
        
        for r_idx, p in enumerate(products):
            row = ctk.CTkFrame(self.list_frame, height=40, corner_radius=0, fg_color="transparent")
            row.pack(fill="x", pady=1)

            # Col 0: Nombre
            ctk.CTkLabel(row, text=p[1], width=self.col_widths[0], anchor="center", font=ctk.CTkFont(weight="bold"), text_color=self.color_green).grid(row=0, column=0, padx=5)
            
            # Col 1: Descripcion
            desc_text = p[2] if p[2] else "-"
            if len(desc_text) > 30: desc_text = desc_text[:27] + "..."
            ctk.CTkLabel(row, text=desc_text, width=self.col_widths[1], anchor="center").grid(row=0, column=1, padx=5)
            
            # Col 2: Categoria
            ctk.CTkLabel(row, text=p[3] or "-", width=self.col_widths[2], anchor="center").grid(row=0, column=2, padx=5)

            # Col 3: Precio
            price_txt = f"{p[4]:.2f} €" if p[4] is not None else "-"
            ctk.CTkLabel(row, text=price_txt, width=self.col_widths[3], anchor="center").grid(row=0, column=3, padx=5)
            
            # Col 4: Billing
            ctk.CTkLabel(row, text=p[5] or "-", width=self.col_widths[4], anchor="center").grid(row=0, column=4, padx=5)

            # col 5: status
            status_color = self.color_green if p[6] == "Active" else "gray"
            ctk.CTkLabel(row, text=p[6] or "-", width=self.col_widths[5], anchor="center", text_color=status_color, font=ctk.CTkFont(weight="bold")).grid(row=0, column=5, padx=5)

            # col 6: url
            url_txt = "View link" if p[7] else "-"
            url_lbl = ctk.CTkLabel(row, text=url_txt, width=self.col_widths[6], anchor="center", 
                                 text_color="#5dade2" if p[7] else "gray", cursor="hand2" if p[7] else "")
            url_lbl.grid(row=0, column=6, padx=5)
            if p[7]: url_lbl.bind("<Button-1>", lambda e, u=p[7]: self.open_link(u))

            #Col 7: actions
            actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[7])
            actions.grid(row=0, column=7, padx=5)
            ctk.CTkButton(actions, text="", image=self.img_delete, width=28, height=28, fg_color=self.color_brick, hover_color="#7A1F1F",
                          command=lambda p_id=p[0]: self.remove_product(p_id)).pack(expand=True)
            
            #separador
            ctk.CTkFrame(self.list_frame, height=1, fg_color="#2A2A2A").pack(fill="x", padx=10)

    def open_add_product_window(self):
            if not hasattr(self, "add_win") or not self.add_win.winfo_exists():
                self.add_win = AddProductWindow(self)
            self.add_win.focus()
        
    def remove_product(self, product_id):
            if delete_product(product_id): self.refresh_list()