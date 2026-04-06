import customtkinter as ctk
from core.companies import add_company

class AddCompanyWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent) 
        self.parent = parent
        self.title("Register new company")
        self.geometry("450x550")
        self.attributes("-topmost", True)

        self.color_green = "#2E8D1B"
        self.color_silver = "#D9D9D9"

        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Company Details", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_green)
        self.title_label.grid(row=0, column=0, pady=(25,15), sticky="ew")

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx= 40, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)

        

        # formulario
        self.name_entry = self.create_input(self.form_frame, "Company Name", 0)
        self.industry_entry = self.create_input(self.form_frame, "Industry", 1)
        self.size_entry = self.create_input(self.form_frame, "Size", 2)
        self.web_entry = self.create_input(self.form_frame, "Website URL", 3)
        self.li_entry = self.create_input(self.form_frame, "LinkedIn URL", 4)
        self.addr_entry = self.create_input(self.form_frame, "Physical Address",5)

        self.save_btn = ctk.CTkButton(self, text="Save", fg_color=self.color_green, hover_color="#246B15", height=40, 
                                      border_color=self.color_green, command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=30, padx= 40, sticky="ew")
        
    def create_input(self, master, placeholder, row_idx):
        entry = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, border_color=self.color_green)
        entry.grid(row=row_idx, column= 0, pady=8, sticky="ew")
        return entry

    def save_data(self):
        name = self.name_entry.get()
        if not name:
            self.name_entry.configure(text_color="red", border_color="red")
            return
        
        success = add_company(
            name,
            self.industry_entry.get(),
            self.size_entry.get(),
            self.web_entry.get(),
            self.li_entry.get(),
            self.addr_entry.get()
        )

        if success:
            self.parent.refresh_list()
            self.destroy()