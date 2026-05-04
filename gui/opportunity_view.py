import customtkinter as ctk
import os
from PIL import Image
from core.opportunities import get_all_opportunities, search_opportunities, delete_opportunity
from gui.opportunity_popup import AddOpportunityWindow

class OpportunityView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.color_green = "#2E8D1B"
        self.color_silver = "#D9D9D9"
        self.color_header = "#3F3F3F"
        self.color_brick = "#A52A2A"

        self.current_sort = "o.name"
        self.sort_order = "ASC"
        self.header_buttons = {}

        self.load_images()

        # CONFIGURACIÓN DE COLUMNAS
        self.col_widths = [180, 160, 120, 100, 100, 110, 100, 80]
        self.headers_info = [
            ("OPP NAME", "o.name"), 
            ("CLIENT", "c.full_name"), 
            ("STATUS", "o.status"), 
            ("PRIORITY", "o.priority"), 
            ("VALUE (€)", "o.estimated_value"), 
            ("CLOSE DATE", "o.expected_close_date"), 
            ("OWNER", "u.username"),
            ("ACTIONS", None)
        ]

        # BARRA DE HERRAMIENTAS SUPERIOR
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=10, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(self.toolbar, placeholder_text="🔍 Search opportunities...", 
                                        width=300, border_color=self.color_green)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_list())

        self.add_btn = ctk.CTkButton(self.toolbar, text="+ New Opportunity", width=140, 
                                    fg_color=self.color_green, hover_color="#246B15",
                                    command=self.open_add_opportunity_window)
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
                btn.configure(text=f"{original_name}{arrow}")
            else:
                btn.configure(text=original_name)

    def load_images(self):
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        def get_img(name):
            path = os.path.join(base_path, name)
            if os.path.exists(path): return ctk.CTkImage(Image.open(path), size=(16, 16))
            return None
        self.img_delete = get_img("trash.png")

    def get_status_color(self, status):
        colors = {
            "qualification": "gray",
            "proposal": "#5dade2", 
            "evaluation": "#f4d03f", 
            "negotiation": "#fd7600", 
            "closed_won": self.color_green,
            "closed_lost": self.color_brick
        }
        return colors.get(status, self.color_silver)

    def get_priority_color(self, priority):
        colors = {
            "very_high": self.color_brick,
            "medium": "#fd7600",
            "low": "#5dade2",
            "very_low": "gray"
        }
        return colors.get(priority, self.color_silver)

    def format_text(self, text):
        # Formatea textos como 'closed_won' a 'Closed Won'
        if not text: return "-"
        return text.replace("_", " ").title()

    def refresh_list(self):
        for widget in self.list_frame.winfo_children(): widget.destroy()
        
        term = self.search_entry.get()
        # SQL devuelve: 0:id, 1:name, 2:status, 3:priority, 4:value, 5:proposal_date, 6:close_date, 7:contact, 8:company, 9:user
        opps = search_opportunities(term, self.current_sort, self.sort_order) if term else get_all_opportunities(self.current_sort, self.sort_order)

        for r_idx, o in enumerate(opps):
            row = ctk.CTkFrame(self.list_frame, height=40, corner_radius=0, fg_color="transparent")
            row.pack(fill="x", pady=1)
            
            # Col 0: Opp Name
            ctk.CTkLabel(row, text=o[1], width=self.col_widths[0], anchor="center", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5)

            # Col 1: Contact (Mostramos "Contacto - Empresa" si hay empresa)
            client_text = o[7] or "No Contact"
            if o[8]: client_text += f" ({o[8]})"
            # Recortar si es muy largo
            if len(client_text) > 22: client_text = client_text[:19] + "..."
            ctk.CTkLabel(row, text=client_text, width=self.col_widths[1], anchor="center", text_color=self.color_green).grid(row=0, column=1, padx=5)

            # Col 2: Status (Con color)
            s_color = self.get_status_color(o[2])
            ctk.CTkLabel(row, text=self.format_text(o[2]), width=self.col_widths[2], anchor="center", text_color=s_color, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)

            # Col 3: Priority (Con color)
            p_color = self.get_priority_color(o[3])
            ctk.CTkLabel(row, text=self.format_text(o[3]), width=self.col_widths[3], anchor="center", text_color=p_color).grid(row=0, column=3, padx=5)

            # Col 4: Value
            val_txt = f"{o[4]:,.2f} €" if o[4] is not None else "-"
            ctk.CTkLabel(row, text=val_txt, width=self.col_widths[4], anchor="center").grid(row=0, column=4, padx=5)

            # Col 5: Close Date
            ctk.CTkLabel(row, text=o[6] or "-", width=self.col_widths[5], anchor="center").grid(row=0, column=5, padx=5)

            # Col 6: Owner
            ctk.CTkLabel(row, text=o[9] or "Unassigned", width=self.col_widths[6], anchor="center").grid(row=0, column=6, padx=5)

            # Col 7: Actions
            actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[7])
            actions.grid(row=0, column=7, padx=5)
            ctk.CTkButton(actions, text="", image=self.img_delete, width=28, height=28, fg_color=self.color_brick, hover_color="#7A1F1F",
                          command=lambda opp_id=o[0]: self.remove_opportunity(opp_id)).pack(expand=True)

            # Separador
            ctk.CTkFrame(self.list_frame, height=1, fg_color="#2A2A2A").pack(fill="x", padx=10)

    def open_add_opportunity_window(self):
        if not hasattr(self, "add_win") or not self.add_win.winfo_exists():
            self.add_win = AddOpportunityWindow(self)
        self.add_win.focus()

    def remove_opportunity(self, opp_id): 
        if delete_opportunity(opp_id): self.refresh_list()