import customtkinter as ctk
from core.companies import add_company, update_company
from gui.alerts import show_alert

class AddCompanyWindow(ctk.CTkToplevel):
    def __init__(self, parent, company_data=None):
        super().__init__(parent) 
        self.parent = parent
        self.company_data = company_data
        self.company_id = company_data[0] if company_data else None

        title_text = "Edit company" if self.company_id else "Register new company"
        self.title(title_text)
        self.geometry("450x550")
        self.attributes("-topmost", True)

        self.color_green = "#2E8D1B"
        self.color_silver = "#D9D9D9"
        self.color_neon = "#DEFF9A"

        self.grid_columnconfigure(0, weight=1)

        header_text = "Edit Company Details" if self.company_id else "Company Details"
        self.title_label = ctk.CTkLabel(self, text=header_text, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_neon)
        self.title_label.grid(row=0, column=0, pady=(25,15), sticky="ew")

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx= 40, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)

        # formulario
        self.name_entry = self.create_input(self.form_frame, "Company Name *", 0)
        self.industry_entry = self.create_input(self.form_frame, "Industry", 1)
        self.size_entry = self.create_input(self.form_frame, "Size", 2)
        self.web_entry = self.create_input(self.form_frame, "Website URL", 3)
        self.li_entry = self.create_input(self.form_frame, "LinkedIn URL", 4)
        self.addr_entry = self.create_input(self.form_frame, "Physical Address",5)

        btn_text = "Update" if self.company_id else "Save"
        self.save_btn = ctk.CTkButton(self, text=btn_text, fg_color=self.color_green, hover_color=self.color_green, height=40, 
                                      border_color=self.color_neon, command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=30, padx= 40, sticky="ew")
        
        if self.company_data:
            self.populate_data()
        
    def create_input(self, master, placeholder, row_idx):
        entry = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, border_color=self.color_neon)
        entry.grid(row=row_idx, column= 0, pady=8, sticky="ew")
        return entry

    def populate_data(self):
        # id(0), name(1), industry(2), size(3), website(4), linkedin(5), address(6)
        self.name_entry.insert(0, self.company_data[1])
        if self.company_data[2]: self.industry_entry.insert(0, self.company_data[2])
        if self.company_data[3]: self.size_entry.insert(0, self.company_data[3])
        if self.company_data[4]: self.web_entry.insert(0, self.company_data[4])
        if self.company_data[5]: self.li_entry.insert(0, self.company_data[5])
        if self.company_data[6]: self.addr_entry.insert(0, self.company_data[6])

    def save_data(self):
        name = self.name_entry.get()
        if not name.strip():
            self.name_entry.configure(border_color="#A52A2A")
            show_alert(self, "Validation Error", "Company Name is required.")
            return
        self.name_entry.configure(border_color=self.color_green)
        
        if self.company_id:
            success = update_company(self.company_id, name, self.industry_entry.get(), self.size_entry.get(), self.web_entry.get(), self.li_entry.get(), self.addr_entry.get())
        else:
            success = add_company(name, self.industry_entry.get(), self.size_entry.get(), self.web_entry.get(), self.li_entry.get(), self.addr_entry.get())

        if success:
            self.parent.refresh_list()
            self.destroy()