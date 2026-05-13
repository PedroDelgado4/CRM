import customtkinter as ctk
import os
from PIL import Image
from core.finances import get_all_finances, search_finances, delete_finance, get_finance_summary
from gui.finance_popup import FinancePopup
from core.csv_utils import export_table_to_csv

class FinanceView(ctk.CTkFrame):
    def __init__(self, master, user_data):
        super().__init__(master, fg_color="transparent")
        self.user_data = user_data
        
        self.color_green = "#2E8D1B"
        self.color_brick = "#FF0000"
        self.color_header = "#3F3F3F"
        self.color_silver = "#D9D9D9"
        self.color_white = "#FFFFFF"

        self.current_sort = "date"
        self.sort_order = "DESC"
        self.header_buttons = {}

        self.load_images()

        # 1. PANEL DE RESUMEN (Dashboard Financiero)
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.pack(fill="x", padx=10, pady=(0, 20))
        self.build_summary_cards()

        # 2. BARRA DE HERRAMIENTAS
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=10, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(self.toolbar, placeholder_text="🔍 Search transactions...", 
                                        width=300, border_color=self.color_green)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_list())

        self.add_btn = ctk.CTkButton(self.toolbar, text="+ New Entry", width=140, 
                                    fg_color=self.color_green, hover_color="#246B15",
                                    command=self.open_add_finance_window)
        self.add_btn.pack(side="right", padx=5)

        self.export_btn = ctk.CTkButton(
            self.toolbar, text="📥 Export CSV", width=120, 
            fg_color="#3F3F3F", hover_color="#4F4F4F",
            command=self.run_export
        )
        self.export_btn.pack(side="right", padx=5)

        # 3. CABECERA DE TABLA
        self.col_widths = [120, 100, 120, 350, 100]
        self.headers_info = [
            ("DATE", "date"), ("TYPE", "entry_type"), ("AMOUNT", "amount"), 
            ("DESCRIPTION", "description"), ("ACTIONS", None)
        ]

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

        # 4. LISTA
        self.list_frame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.list_frame.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        self.refresh_list()

    def build_summary_cards(self):
        # Card Ingresos
        self.card_income = self.create_card(self.summary_frame, "Total Income", "0.00 €", self.color_green, 0)
        # Card Gastos
        self.card_expense = self.create_card(self.summary_frame, "Total Expense", "0.00 €", self.color_brick, 1)
        # Card Balance
        self.card_balance = self.create_card(self.summary_frame, "Net Balance", "0.00 €", "#3498db", 2)

    def create_card(self, master, title, value, color, col):
        card = ctk.CTkFrame(master, fg_color=self.color_header, corner_radius=10, height=80)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        master.grid_columnconfigure(col, weight=1)
        
        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color=self.color_silver)
        lbl_title.pack(pady=(10, 0))
        
        lbl_value = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"), text_color=color)
        lbl_value.pack(pady=(0, 10))
        return lbl_value

    def update_dashboard(self):
        summary = get_finance_summary()
        self.card_income.configure(text=f"{summary['income']:,.2f} €")
        self.card_expense.configure(text=f"{summary['expense']:,.2f} €")
        
        balance = summary['balance']
        b_color = self.color_green if balance >= 0 else self.color_brick
        self.card_balance.configure(text=f"{balance:,.2f} €", text_color=b_color)

    def load_images(self):
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        def get_img(name):
            path = os.path.join(base_path, name)
            if os.path.exists(path): return ctk.CTkImage(Image.open(path), size=(16, 16))
            return None
        self.img_delete = get_img("trash.png")
        self.img_edit = get_img("edit.png")

    def set_sort(self, key):
        if self.current_sort == key:
            self.sort_order = "DESC" if self.sort_order == "ASC" else "ASC"
        else:
            self.current_sort = key
            self.sort_order = "ASC"
        self.refresh_list()

    def refresh_list(self):
        for widget in self.list_frame.winfo_children(): widget.destroy()
        
        term = self.search_entry.get()
        entries = search_finances(term, self.current_sort, self.sort_order) if term else get_all_finances(self.current_sort, self.sort_order)

        for e in entries:
            row = ctk.CTkFrame(self.list_frame, height=40, corner_radius=0, fg_color="transparent")
            row.pack(fill="x", pady=1)

            # Col 0: Fecha
            ctk.CTkLabel(row, text=e[4], width=self.col_widths[0], anchor="center").grid(row=0, column=0, padx=5)

            # Col 1: Tipo
            t_color = self.color_green if e[1] == "income" else self.color_brick
            ctk.CTkLabel(row, text=e[1].upper(), width=self.col_widths[1], anchor="center", text_color=t_color, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5)

            # Col 2: Cantidad
            amount_text = f"{e[2]:,.2f} €"
            ctk.CTkLabel(row, text=amount_text, width=self.col_widths[2], anchor="center", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)

            # Col 3: Descripción
            desc = e[3] if len(e[3]) < 45 else e[3][:42] + "..."
            ctk.CTkLabel(row, text=desc, width=self.col_widths[3], anchor="w").grid(row=0, column=3, padx=15)

            # Col 4: Acciones
            actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[4])
            actions.grid(row=0, column=4, padx=5)
            
            btn_container = ctk.CTkFrame(actions, fg_color="transparent")
            btn_container.pack(expand=True)

            ctk.CTkButton(btn_container, text="", image=self.img_edit, width=28, height=28, fg_color="#f39c12", hover_color="#d68910",
                          command=lambda eid=e[0]: self.open_add_finance_window(eid)).pack(side="left", padx=2)

            if self.user_data[2] == 'admin':
                ctk.CTkButton(btn_container, text="", image=self.img_delete, width=28, height=28, fg_color=self.color_brick, hover_color="#7A1F1F",
                              command=lambda eid=e[0]: self.remove_entry(eid)).pack(side="left", padx=2)

            ctk.CTkFrame(self.list_frame, height=1, fg_color="#2A2A2A").pack(fill="x", padx=10)
        
        self.update_dashboard()

    def open_add_finance_window(self, entry_id=None):
        if not hasattr(self, "add_win") or not self.add_win.winfo_exists():
            self.add_win = FinancePopup(self, entry_id)
        self.add_win.focus()

    def remove_entry(self, entry_id):
        if delete_finance(entry_id): self.refresh_list()

    def run_export(self):
        data = get_all_finances(self.current_sort, self.sort_order)
        headers = ["ID", "Type", "Amount", "Description", "Date"]
        export_table_to_csv(headers, data, "finance_report")