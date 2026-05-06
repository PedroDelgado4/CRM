import customtkinter as ctk
from core.opportunities import add_opportunity
from core.contacts import get_all_contacts
from core.companies import get_all_companies

class AddOpportunityWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("New Opportunity")
        self.geometry("500x700")
        self.attributes("-topmost", True)
        
        self.color_green = "#2E8D1B"
        
        # --- CARGA DE DATOS RELACIONALES ---
        # 1. Empresas
        self.company_data = get_all_companies(sort_by="name", order="ASC")
        self.company_dict = {comp[1]: comp[0] for comp in self.company_data}
        company_names = ["-- Select Company --"] + list(self.company_dict.keys())

        # 2. Contactos 
        self.contact_data = get_all_contacts(sort_by="c.full_name", order="ASC")
        self.contact_dict = {}
        for c in self.contact_data:
            display_name = f"{c[1]} ({c[2]})" if c[2] else c[1]
            self.contact_dict[display_name] = c[0]
        contact_names = ["-- Select Contact --"] + list(self.contact_dict.keys())

        # 3. Usuarios
        if hasattr(self.parent.master, "all_users"):
             self.user_dict = {user[1]: user[0] for user in self.parent.master.all_users}
        else:
             from core.auth import get_all_users
             self.user_dict = {user[1]: user[0] for user in get_all_users()}
        user_names = ["-- Unassigned --"] + list(self.user_dict.keys())

        # --- MAPEO DE ESTADOS Y PRIORIDADES ---
        self.status_map = {
            "Qualification": "qualification",
            "Proposal": "proposal",
            "Evaluation": "evaluation",
            "Negotiation": "negotiation",
            "Closed Won": "closed_won",
            "Closed Lost": "closed_lost"
        }
        self.priority_map = {
            "Very High": "very_high",
            "High": "high",
            "Medium": "medium",
            "Low": "low",
            "Very Low": "very_low"
        }

        # --- REJILLA PRINCIPAL ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Opportunity Details", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_green)
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        # Contenedor Scrollable para el formulario
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, padx=40, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # 1. Nombre (Obligatorio)
        self.name_entry = self.create_input(self.scroll_frame, "Opportunity Name *", 0)

        # 2. Relaciones (Empresa y Contacto)
        self.company_var = ctk.StringVar(value="-- Select Company --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.company_var, values=company_names, fg_color="#3F3F3F", button_color=self.color_green).grid(row=1, column=0, pady=8, sticky="ew")

        self.contact_var = ctk.StringVar(value="-- Select Contact --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.contact_var, values=contact_names, fg_color="#3F3F3F", button_color=self.color_green).grid(row=2, column=0, pady=8, sticky="ew")

        # 3. Estado
        self.status_var = ctk.StringVar(value="Qualification")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.status_var, values=list(self.status_map.keys()), fg_color="#3F3F3F", button_color=self.color_green).grid(row=3, column=0, pady=8, sticky="ew")

        # 4. Prioridad
        self.priority_var = ctk.StringVar(value="Medium")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.priority_var, values=list(self.priority_map.keys()), fg_color="#3F3F3F", button_color=self.color_green).grid(row=4, column=0, pady=8, sticky="ew")

        # 5. Valor Estimado
        self.value_entry = self.create_input(self.scroll_frame, "Estimated Value (€)", 5)

        # 6. Fechas (Texto por ahora DD/MM/YYYY)
        self.proposal_date_entry = self.create_input(self.scroll_frame, "Proposal Deadline (DD/MM/YYYY)", 6)
        self.close_date_entry = self.create_input(self.scroll_frame, "Expected Close Date (DD/MM/YYYY)", 7)

        # 7. Asignado a
        self.assign_var = ctk.StringVar(value="-- Unassigned --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.assign_var, values=user_names, fg_color="#3F3F3F", button_color=self.color_green).grid(row=8, column=0, pady=8, sticky="ew")

        # Botón Guardar 
        self.save_btn = ctk.CTkButton(self, text="Save Opportunity", fg_color=self.color_green, hover_color="#246B15", height=40, font=ctk.CTkFont(weight="bold"), command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=20, padx=40, sticky="ew")

    def create_input(self, master, placeholder, row_idx):
        entry = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, border_color=self.color_green)
        entry.grid(row=row_idx, column=0, pady=8, sticky="ew")
        return entry

    def save_data(self):
        # 1. Validar Nombre
        name = self.name_entry.get()
        if not name.strip():
            self.name_entry.configure(border_color="#A52A2A")
            return
        self.name_entry.configure(border_color=self.color_green)

        # 2. Validar Valor Numérico
        val_raw = self.value_entry.get().strip()
        est_value = 0.0
        if val_raw:
            try:
                est_value = float(val_raw.replace(",", "."))
                self.value_entry.configure(border_color=self.color_green)
            except ValueError:
                self.value_entry.configure(border_color="#A52A2A")
                return

        # 3. Mapear Desplegables a IDs y Enums
        comp_id = self.company_dict.get(self.company_var.get())
        cont_id = self.contact_dict.get(self.contact_var.get())
        user_id = self.user_dict.get(self.assign_var.get())
        
        db_status = self.status_map.get(self.status_var.get(), "qualification")
        db_priority = self.priority_map.get(self.priority_var.get(), "medium")

        # 4. Guardar
        success = add_opportunity(
            name=name,
            status=db_status,
            priority=db_priority,
            estimated_value=est_value,
            proposal_deadline=self.proposal_date_entry.get(),
            expected_close_date=self.close_date_entry.get(),
            contact_id=cont_id,
            company_id=comp_id,
            assigned_to=user_id
        )

        if success:
            self.parent.refresh_list()
            self.destroy()