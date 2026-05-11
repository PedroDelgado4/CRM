import customtkinter as ctk
from datetime import date
from core.finances import add_finance_entry, update_finance_entry, get_finance_by_id

class AddFinanceWindow(ctk.CTkToplevel):
    def __init__(self, parent, entry_id=None):
        super().__init__(parent)
        self.parent = parent
        self.entry_id = entry_id
        
        title_text = "Edit Transaction" if self.entry_id else "New Transaction"
        self.title(title_text)
        self.geometry("400x450")
        self.attributes("-topmost", True)
        
        self.color_green = "#2E8D1B"
        self.color_brick = "#A52A2A"

        self.grid_columnconfigure(0, weight=1)

        header_text = "Edit Finance Entry" if self.entry_id else "Log Finance Entry"
        self.title_label = ctk.CTkLabel(self, text=header_text, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_green)
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx=40, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)

        # 1. Selector de Tipo (Income / Expense)
        self.type_var = ctk.StringVar(value="income")
        self.type_segmented = ctk.CTkSegmentedButton(
            self.form_frame, 
            values=["income", "expense"], 
            variable=self.type_var, 
            selected_color=self.color_green, 
            selected_hover_color="#246B15",
            command=self.update_segment_color
        )
        self.type_segmented.grid(row=0, column=0, pady=(10, 20), sticky="ew")

        # 2. Cantidad y Fecha
        self.amount_entry = self.create_input(self.form_frame, "Amount (€) *", 1)
        
        self.date_entry = self.create_input(self.form_frame, "Date (YYYY-MM-DD)", 2)
        # rellenamos la fecha de hoy por defecto
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        # 3. Descrip
        self.desc_entry = self.create_input(self.form_frame, "Description / Concept *", 3)

        btn_text = "Update Transaction" if self.entry_id else "Save Transaction"
        self.save_btn = ctk.CTkButton(self, text=btn_text, fg_color=self.color_green, hover_color="#246B15", height=40, font=ctk.CTkFont(weight="bold"), command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=30, padx=40, sticky="ew")

        if self.entry_id:
            self.populate_data()

    def create_input(self, master, placeholder, row_idx):
        entry = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, border_color=self.color_green)
        entry.grid(row=row_idx, column=0, pady=8, sticky="ew")
        return entry

    def update_segment_color(self, selected_val):
        # rojo si es un gasto, verde si es ingreso
        if selected_val == "expense":
            self.type_segmented.configure(selected_color=self.color_brick, selected_hover_color="#7A1F1F")
        else:
            self.type_segmented.configure(selected_color=self.color_green, selected_hover_color="#246B15")

    def populate_data(self):
        raw_entry = get_finance_by_id(self.entry_id)
        if not raw_entry: return
        
        # 0:id, 1:type, 2:amount, 3:description, 4:date
        self.type_var.set(raw_entry[1])
        self.update_segment_color(raw_entry[1])
        
        if raw_entry[2] is not None: self.amount_entry.insert(0, str(raw_entry[2]))
        if raw_entry[3]: self.desc_entry.insert(0, raw_entry[3])
        
        if raw_entry[4]: 
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, raw_entry[4])

    def save_data(self):
        val_raw = self.amount_entry.get().strip()
        amount = 0.0
        if not val_raw:
            self.amount_entry.configure(border_color=self.color_brick)
            return
        try:
            amount = float(val_raw.replace(",", "."))
            self.amount_entry.configure(border_color=self.color_green)
        except ValueError:
            self.amount_entry.configure(border_color=self.color_brick)
            return

        desc = self.desc_entry.get().strip()
        if not desc:
            self.desc_entry.configure(border_color=self.color_brick)
            return
        self.desc_entry.configure(border_color=self.color_green)

        e_type = self.type_var.get()
        e_date = self.date_entry.get().strip()

        if self.entry_id:
            success = update_finance_entry(self.entry_id, e_type, amount, desc, e_date)
        else:
            success = add_finance_entry(e_type, amount, desc, e_date)

        if success:
            self.parent.refresh_list()
            self.destroy()