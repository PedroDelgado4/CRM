import customtkinter as ctk
from core.contacts import add_contact, update_contact, get_contact_by_id
from core.companies import get_all_companies
from gui.alerts import show_alert

class AddContactWindow(ctk.CTkToplevel):
    def __init__(self, parent, contact_id=None):
        super().__init__(parent) 
        self.parent = parent
        self.contact_id = contact_id
        
        title_text = "Edit Contact" if self.contact_id else "Register new contact"
        self.title(title_text)
        self.geometry("450x650")
        self.attributes("-topmost", True)

        self.color_green = "#2E8D1B"
        self.color_neon = "#DEFF9A"


        # --- Carga de datos para desplegables ---
        self.company_data = get_all_companies(sort_by="name", order="ASC")
        self.company_dict = {comp[1]: comp[0] for comp in self.company_data}
        company_names = ["--- Select company ---"] + list(self.company_dict.keys())

        if hasattr(self.parent, "all_users"):
            self.user_dict = {user[1]: user[0] for user in self.parent.all_users}
        else:
            from core.auth import get_all_users
            self.user_dict = {user[1]: user[0] for user in get_all_users()}
            
        user_names = ["--- Unassigned ---"] + list(self.user_dict.keys())

        # --- rejilla principal ---
        self.grid_columnconfigure(0, weight=1)

        header_text = "Edit Contact Details" if self.contact_id else "Contact Details"
        self.title_label = ctk.CTkLabel(self, text=header_text, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_neon)
        self.title_label.grid(row=0, column=0, pady=(20,10), sticky="ew")

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx= 40, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)

        self.name_entry = self.create_input(self.form_frame, "Full name *", 0)

        self.company_var = ctk.StringVar(value="--- Select company ---")
        self.company_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.company_var, values=company_names, 
                                              fg_color="#3F3F3F", button_color="#223E22", button_hover_color="#246b15")
        self.company_menu.grid(row=1, column=0, pady=8, sticky="ew")

        self.email_entry = self.create_input(self.form_frame, "Email address", 2)
        self.phone_entry = self.create_input(self.form_frame, "Phone number", 3)
        self.position_entry = self.create_input(self.form_frame, "Job position", 4)
        self.linkedin_entry = self.create_input(self.form_frame, "LinkedIn URL", 5)

        self.vip_var = ctk.IntVar(value=0)
        self.vip_switch = ctk.CTkSwitch(self.form_frame, text="Mark as VIP contact", variable=self.vip_var, progress_color=self.color_neon)
        self.vip_switch.grid(row=6, column=0, pady=12, sticky="w")

        self.assign_var = ctk.StringVar(value="--- Unassigned ---")
        self.assign_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.assign_var, values=user_names, 
                                              fg_color="#3F3F3F", button_color="#223E22", button_hover_color="#246b15")
        self.assign_menu.grid(row=7, column=0, pady=8, sticky="ew")

        btn_text = "Update contact" if self.contact_id else "Save contact"
        self.save_btn = ctk.CTkButton(self, text=btn_text, fg_color=self.color_green, hover_color="#246b15", height=40,
                                      font=ctk.CTkFont(weight="bold"), command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=25, padx = 40, sticky="ew")
        
        if self.contact_id:
            self.populate_data()

    def create_input(self, master, placeholder, row_idx):
        entry = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, border_color=self.color_neon)
        entry.grid(row=row_idx, column= 0, pady=8, sticky="ew")
        return entry

    def populate_data(self):
        raw_contact = get_contact_by_id(self.contact_id)
        if not raw_contact: return
        
        # 0:id, 1:name, 2:company_id, 3:vip, 4:email, 5:phone, 6:position, 7:linkedin, 8:assigned_to
        self.name_entry.insert(0, raw_contact[1])
        
        if raw_contact[2]:
            for k, v in self.company_dict.items():
                if v == raw_contact[2]: self.company_var.set(k)
                
        self.vip_var.set(raw_contact[3] if raw_contact[3] else 0)
        if self.vip_var.get() == 1: self.vip_switch.select()
        else: self.vip_switch.deselect()
            
        if raw_contact[4]: self.email_entry.insert(0, raw_contact[4])
        if raw_contact[5]: self.phone_entry.insert(0, raw_contact[5])
        if raw_contact[6]: self.position_entry.insert(0, raw_contact[6])
        if raw_contact[7]: self.linkedin_entry.insert(0, raw_contact[7])
        
        if raw_contact[8]:
            for k, v in self.user_dict.items():
                if v == raw_contact[8]: self.assign_var.set(k)

    def save_data(self):
        name = self.name_entry.get()
        if not name or name.strip() == "":
            self.name_entry.configure(border_color="#A52A2A")
            return
        self.name_entry.configure(border_color=self.color_green)
        
        comp_id = self.company_dict.get(self.company_var.get())
        assign_id = self.user_dict.get(self.assign_var.get())

        if self.contact_id:
            success = update_contact(self.contact_id, name, comp_id, self.vip_var.get(), self.email_entry.get(), 
                                     self.phone_entry.get(), self.position_entry.get(), self.linkedin_entry.get(), assign_id)
        else:
            success = add_contact(name, comp_id, self.vip_var.get(), self.email_entry.get(), self.phone_entry.get(), 
                                  self.position_entry.get(), self.linkedin_entry.get(), assign_id)

        if success:
            self.parent.refresh_list()
            self.destroy()