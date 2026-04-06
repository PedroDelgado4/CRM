import customtkinter as ctk
from core.contacts import add_contact
from core.companies import get_all_companies

class AddContactWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent) 
        self.parent = parent
        self.title("Register new contact")
        self.geometry("450x650")
        self.attributes("-topmost", True)

        self.color_green = "#2E8D1B"

        # --- Carga de datos para desplegables ---

        # 1. empresas
        self.company_data = get_all_companies(sort_by="name", order="ASC")

        # dic para traducir nombre a ID
        self.company_dict = {comp[1]: comp[0] for comp in self.company_data}
        company_names = ["--- Select company ---"] + list(self.company_dict.keys())

        # responsable
        self.user_dict = {user[1]: user[0] for user in self.parent.all_users}
        user_names = ["--- Unassigned ---"] + list(self.user_dict.keys())

        # --- rejilla principal ---
        self.grid_columnconfigure(0, weight=1)

        # titulo
        self.title_label = ctk.CTkLabel(self, text="Contact Details", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_green)
        self.title_label.grid(row=0, column=0, pady=(20,10), sticky="ew")

        # contenedor del form
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx= 40, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)

        # nombre
        self.name_entry = self.create_input(self.form_frame, "Full name", 0)

        # desplegable de empresas
        self.company_var = ctk.StringVar(value="--- Select company ---")
        self.company_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.company_var, values=company_names, 
                                              fg_color="#3F3F3F", button_color=self.color_green, button_hover_color="#246b15")
        self.company_menu.grid(row=1, column=0, pady=8, sticky="ew")

        # resto de campos

        self.email_entry = self.create_input(self.form_frame, "Email address", 2)
        self.phone_entry = self.create_input(self.form_frame, "Phone number", 3)
        self.position_entry = self.create_input(self.form_frame, "Job position", 4)
        self.linkedin_entry = self.create_input(self.form_frame, "LinkedIn URL", 5)

        # switch para VIP
        self.vip_var = ctk.IntVar(value=False)
        self.vip_switch = ctk.CTkSwitch(self.form_frame, text="Mark as VIP contact", variable=self.vip_var, progress_color=self.color_green)
        self.vip_switch.grid(row=6, column=0, pady=12, sticky="w")

        # desplegrable de responsable
        self.assign_var = ctk.StringVar(value="--- Unassigned ---")
        self.assign_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.assign_var, values=user_names, 
                                              fg_color="#3F3F3F", button_color=self.color_green, button_hover_color="#246b15")
        self.assign_menu.grid(row=7, column=0, pady=8, sticky="ew")

        # boton guardar
        self.save_btn = ctk.CTkButton(self, text="Save contact", fg_color=self.color_green, hover_color="#246b15", height=40,
                                      font=ctk.CTkFont(weight="bold"), command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=25, padx = 40, sticky="ew")

    def create_input(self, master, placeholder, row_idx):
        entry = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, border_color=self.color_green)
        entry.grid(row=row_idx, column= 0, pady=8, sticky="ew")
        return entry

    def save_data(self):
        # validar nombre
        name = self.name_entry.get()
        if not name or name.strip() == "" or name.isspace():
            self.name_entry.configure(border_color="#A52A2A")
            return
        
        # traducir nombres a ids
        comp_name = self.company_var.get()
        comp_id = self.company_dict.get(comp_name)

        assign_name = self.assign_var.get()
        assign_id = self.user_dict.get(assign_name)

        # guardar en la db
        success = add_contact(
            full_name=name,
            company_id=comp_id,
            is_vip=self.vip_var.get(),
            email=self.email_entry.get(),
            phone=self.phone_entry.get(),
            position=self.position_entry.get(),
            linkedin=self.linkedin_entry.get(),
            assigned_to=assign_id
        )

        if success:
            self.parent.refresh_list()
            self.destroy()






        




