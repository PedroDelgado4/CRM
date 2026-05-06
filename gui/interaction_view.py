import customtkinter as ctk
import os
from PIL import Image
from core.interactions import get_all_interactions, search_interactions, delete_interaction
from gui.interaction_popup import AddInteractionWindow

class InteractionView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
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
        # SQL devuelve: 0:id, 1:note, 2:type, 3:date_time, 4:status, 5:reminder, 6:contact_name, 7:opp_name
        interactions = search_interactions(term, self.current_sort, self.sort_order) if term else get_all_interactions(self.current_sort, self.sort_order)

        for r_idx, i in enumerate(interactions):
            row = ctk.CTkFrame(self.list_frame, height=40, corner_radius=0, fg_color="transparent")
            row.pack(fill="x", pady=1)
            
            # Col 0: Date & Time (SQLite devuelve ej: "2024-05-14 10:30:00")
            dt_text = i[3] if i[3] else "-"
            # Limpiamos los milisegundos si SQLite los devuelve
            if "." in dt_text: dt_text = dt_text.split(".")[0]
            ctk.CTkLabel(row, text=dt_text, width=self.col_widths[0], anchor="center", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5)

            # Col 1: Notes (Recortada)
            note_text = i[1] or "-"
            if len(note_text) > 35: note_text = note_text[:32] + "..."
            ctk.CTkLabel(row, text=note_text, width=self.col_widths[1], anchor="w").grid(row=0, column=1, padx=5)

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
            actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[6])
            actions.grid(row=0, column=6, padx=5)
            ctk.CTkButton(actions, text="", image=self.img_delete, width=28, height=28, fg_color=self.color_brick, hover_color="#7A1F1F",
                          command=lambda inter_id=i[0]: self.remove_interaction(inter_id)).pack(expand=True)

            # Separador
            ctk.CTkFrame(self.list_frame, height=1, fg_color="#2A2A2A").pack(fill="x", padx=10)

    def open_add_interaction_window(self):
        if not hasattr(self, "add_win") or not self.add_win.winfo_exists():
            self.add_win = AddInteractionWindow(self)
        self.add_win.focus()

    def remove_interaction(self, inter_id): 
        if delete_interaction(inter_id): self.refresh_list()