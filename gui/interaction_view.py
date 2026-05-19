import customtkinter as ctk
import os
from PIL import Image
from core.interactions import get_all_interactions, search_interactions, delete_interaction, get_interaction_products
from gui.interaction_popup import AddInteractionWindow
from core.csv_utils import export_table_to_csv

class InteractionView(ctk.CTkFrame):
    def __init__(self, master, user_data):
        super().__init__(master, fg_color="transparent")
        self.user_data = user_data
        
        self.color_green = "#2E8D1B"
        self.color_silver = "#797575"
        self.color_header = "#3F3F3F"
        self.color_brick = "#A52A2A"
        self.color_white = "#D9D9D9"

        # orden por defecto: fecha descendente
        self.current_sort = "i.date_time"
        self.sort_order = "DESC"
        self.header_buttons = {}

        self.load_images()

        # CONFIGURACIÓN DE COLUMNAS (Total ~950px)
        self.col_widths = [140, 240, 100, 120, 100, 150, 80]
        self.headers_info = [
            ("DATE & TIME", "i.date_time"), 
            ("NOTES", "i.note"), 
            ("TYPE", "i.type"), 
            ("CONTACT", "c.full_name"), 
            ("STATUS", "i.status"), 
            ("OPPORTUNITY", "o.name"), 
            ("ACTIONS", None)
        ]

        # BARRA DE HERRAMIENTAS SUPERIOR
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=10, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(self.toolbar, placeholder_text="🔍 Search interactions...", 
                                        width=300, border_color=self.color_green)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_list())

        self.add_btn = ctk.CTkButton(self.toolbar, text="+ Log Interaction", width=140, 
                                    fg_color=self.color_green, hover_color="#246B15",
                                    command=self.open_add_interaction_window)
        self.add_btn.pack(side="right", padx=5)
        
        self.export_btn = ctk.CTkButton(self.toolbar, text="📥 Export CSV", width=110, 
                                    fg_color="#3F3F3F", hover_color="#4F4F4F",
                                    command=self.run_export)
        self.export_btn.pack(side="right", padx=5)

        self.type_filter_var = ctk.StringVar(value="All Types")
        self.type_filter_combo = ctk.CTkComboBox(
            self.toolbar, 
            variable=self.type_filter_var, 
            values=["All Types", "Call", "Email", "Meeting", "Message", "Other"],
            width=150,
            fg_color="#3F3F3F",
            button_color=self.color_green,
            command=lambda e: self.refresh_list()
        )
        self.type_filter_combo.pack(side="left", padx=5)

        # CABECERA
        self.header_frame = ctk.CTkFrame(self, height=35, corner_radius=0, fg_color=self.color_header)
        self.header_frame.pack(fill="x", padx=10)

        for i, (text, sort_key) in enumerate(self.headers_info):
            if sort_key:
                btn = ctk.CTkButton(self.header_frame, text=text, fg_color="transparent", 
                                   text_color=self.color_white, font=ctk.CTkFont(size=11, weight="bold"),
                                   width=self.col_widths[i], anchor="center", corner_radius=0,
                                   hover_color="#4F4F4F", command=lambda k=sort_key: self.set_sort(k))
                btn.grid(row=0, column=i, padx=5, pady=5)
                self.header_buttons[sort_key] = btn
            else:
                lbl = ctk.CTkLabel(self.header_frame, text=text, text_color=self.color_white, 
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
        self.img_edit = get_img("edit.png")

    def get_type_color(self, type_str):
        colors = {
            "call": "#3498db",     
            "email": "#9b59b6",     
            "meeting": "#fd7600",   
            "message": "#2ecc71"    
        }
        return colors.get(type_str.lower() if type_str else "", self.color_silver)

    def format_text(self, text):
        if not text: return "-"
        return text.replace("_", " ").title()

    def refresh_list(self):
        for widget in self.list_frame.winfo_children(): widget.destroy()
        
        term = self.search_entry.get()
        
        # Mapeo del filtro
        raw_filter = self.type_filter_var.get()
        db_filter_map = {
            "All Types": "All",
            "Call": "call",
            "Email": "email",
            "Meeting": "meeting",
            "Message": "message",
            "Other": "other"
        }
        type_val = db_filter_map.get(raw_filter, "All")

        if term:
            interactions = search_interactions(term, self.current_sort, self.sort_order, type_val)
        else:
            interactions = get_all_interactions(self.current_sort, self.sort_order, type_val)

        for r_idx, i in enumerate(interactions):
            row = ctk.CTkFrame(self.list_frame, height=45, corner_radius=0, fg_color="transparent")
            row.pack(fill="x", pady=1)

            # Cada columna tendrá exactamente el ancho de la cabecera
            for col_idx, width in enumerate(self.col_widths):
                row.grid_columnconfigure(col_idx, minsize=width, weight=0)
            
            # Col 0: Date & Time
            dt_text = i[3] if i[3] else "-"
            if "." in dt_text: dt_text = dt_text.split(".")[0]
            ctk.CTkLabel(row, text=dt_text, width=self.col_widths[0], anchor="center", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5)

            # Col 1: Notes + Productos Tratados
            note_text = i[1] or "-"
            if len(note_text) > 35: note_text = note_text[:32] + "..."
            
            linked_prods = get_interaction_products(i[0])
            prod_txt = "Discussed: " + ", ".join([lp[1] for lp in linked_prods]) if linked_prods else ""
            
            # BLOQUEO DE TAMAÑO EN EL CONTENEDOR DE NOTAS
            note_container = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[1], height=40)
            note_container.pack_propagate(False) # Prohíbe que el contenedor se encoja o estire
            note_container.grid(row=0, column=1, padx=5, sticky="w")
            
            ctk.CTkLabel(note_container, text=note_text, anchor="w").pack(fill="x")
            if prod_txt:
                ctk.CTkLabel(note_container, text=prod_txt, anchor="w", font=ctk.CTkFont(size=10), text_color="#5dade2").pack(fill="x")

            # Col 2: Type (Con color)
            t_color = self.get_type_color(i[2])
            ctk.CTkLabel(row, text=self.format_text(i[2]), width=self.col_widths[2], anchor="center", text_color=t_color).grid(row=0, column=2, padx=5)

            # Col 3: Contact Name
            ctk.CTkLabel(row, text=i[6] or "-", width=self.col_widths[3], anchor="center", text_color=self.color_green).grid(row=0, column=3, padx=5)

            # Col 4: Status
            s_color = self.color_green if i[4] == "completed" else self.color_silver
            if i[4] == "cancelled": s_color = self.color_brick
            ctk.CTkLabel(row, text=self.format_text(i[4]), width=self.col_widths[4], anchor="center", text_color=s_color).grid(row=0, column=4, padx=5)

            # Col 5: Opportunity Name
            opp_text = i[7] or "-"
            if len(opp_text) > 20: opp_text = opp_text[:17] + "..."
            ctk.CTkLabel(row, text=opp_text, width=self.col_widths[5], anchor="center").grid(row=0, column=5, padx=5)

            # Col 6: Actions
            # BLOQUEO DE TAMAÑO EN EL CONTENEDOR DE ACCIONES
            actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[6], height=35)
            actions.pack_propagate(False) 
            actions.grid(row=0, column=6, padx=5)
            
            btn_container = ctk.CTkFrame(actions, fg_color="transparent")
            btn_container.pack(expand=True)
            
            ctk.CTkButton(btn_container, text="", image=self.img_edit, width=28, height=28, fg_color="#f39c12", hover_color="#d68910",
                          command=lambda inter_id=i[0]: self.open_add_interaction_window(inter_id)).pack(side="left", padx=2)

            if self.user_data[2] == 'admin':
                ctk.CTkButton(btn_container, text="", image=self.img_delete, width=28, height=28, fg_color=self.color_brick, hover_color="#7A1F1F",
                              command=lambda inter_id=i[0]: self.remove_interaction(inter_id)).pack(side="left", padx=2)

            # Separador
            ctk.CTkFrame(self.list_frame, height=1, fg_color="#2A2A2A").pack(fill="x", padx=10)

    def open_add_interaction_window(self, interaction_id=None):
        if not hasattr(self, "add_win") or not self.add_win.winfo_exists():
            self.add_win = AddInteractionWindow(self, interaction_id)
        self.add_win.focus()

    def remove_interaction(self, inter_id): 
        if delete_interaction(inter_id): self.refresh_list()

    def run_export(self):
        from core.interactions import get_all_interactions
        data = get_all_interactions(self.current_sort, self.sort_order)
        # El SQL devuelve: id, note, type, date_time, status, reminder, contact_name, opp_name
        headers = ["ID", "Notes", "Type", "Date & Time", "Status", "Reminder Date", "Contact Name", "Opportunity Name"]
        export_table_to_csv(headers, data, "interactions_export")