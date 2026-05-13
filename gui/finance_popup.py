import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from core.finances import add_finance_entry, update_finance_entry, get_finance_by_id

class FinancePopup(ctk.CTkToplevel):
    def __init__(self, master, refresh_callback, finance_id=None):
        super().__init__(master)
        self.refresh_callback = refresh_callback
        self.finance_id = finance_id
        
        title = "Edit Finance Record" if finance_id else "New Finance Record"
        self.title(f"CRM FDT - {title}")
        self.geometry("400x350")
        self.grab_set()

        self.bg_color = "#2b2b2b"
        self.input_bg = "#3F3F3F"
        self.green_accent = "#2E8D1B"

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Type
        ctk.CTkLabel(form_frame, text="Type:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.type_combo = ctk.CTkComboBox(form_frame, values=["income", "expense"], fg_color=self.input_bg, button_color=self.green_accent)
        self.type_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # 2. Amount
        ctk.CTkLabel(form_frame, text="Amount (€):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.amount_entry = ctk.CTkEntry(form_frame, fg_color=self.input_bg)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # 3. Description
        ctk.CTkLabel(form_frame, text="Description:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.desc_entry = ctk.CTkEntry(form_frame, fg_color=self.input_bg)
        self.desc_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # 4. Date (tkcalendar DateEntry)
        ctk.CTkLabel(form_frame, text="Date:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.date_entry = DateEntry(
            form_frame, width=20, 
            background=self.input_bg, foreground='white', borderwidth=0,
            selectbackground=self.green_accent, selectforeground='white',
            normalbackground=self.bg_color, normalforeground='white',
            headersbackground=self.input_bg, headersforeground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.date_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        if self.finance_id:
            self.load_data()

        self.save_btn = ctk.CTkButton(self, text="Save", fg_color=self.green_accent, hover_color="#246B15", command=self.save_finance)
        self.save_btn.pack(pady=10)

    def load_data(self):
        record = get_finance_by_id(self.finance_id)
        if not record: return
        
        self.type_combo.set(record[1])
        self.amount_entry.insert(0, str(record[2]))
        if record[3]: self.desc_entry.insert(0, record[3])
        
        if record[4]:
            try:
                self.date_entry.set_date(datetime.strptime(record[4], '%Y-%m-%d').date())
            except ValueError: pass

    def save_finance(self):
        f_type = self.type_combo.get()
        desc = self.desc_entry.get().strip()
        
        try:
            amount = float(self.amount_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")
            return

        date_val = self.date_entry.get_date().strftime('%Y-%m-%d')

        if self.finance_id:
            success = update_finance_entry(self.finance_id, f_type, amount, desc, date_val)
        else:
            success = add_finance_entry(f_type, amount, desc, date_val)

        if success:
            self.refresh_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save finance record.")