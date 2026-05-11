import customtkinter as ctk
from core.opportunities import add_opportunity, update_opportunity, get_opportunity_by_id, link_product_to_opportunity, unlink_all_products_from_opportunity, get_opportunity_products
from core.contacts import get_all_contacts
from core.companies import get_all_companies
from core.products import get_all_products
from gui.alerts import show_alert

class AddOpportunityWindow(ctk.CTkToplevel):
    def __init__(self, parent, opp_id=None):
        super().__init__(parent)
        self.parent = parent
        self.opp_id = opp_id
        self.product_checkboxes = {} 
        
        title_text = "Edit Opportunity" if self.opp_id else "New Opportunity"
        self.title(title_text)
        self.geometry("550x850") 
        self.attributes("-topmost", True)
        
        self.color_green = "#2E8D1B"
        
        # --- CARGA DE DATOS RELACIONALES ---
        self.company_data = get_all_companies(sort_by="name", order="ASC")
        self.company_dict = {comp[1]: comp[0] for comp in self.company_data}
        company_names = ["-- Select Company --"] + list(self.company_dict.keys())

        self.contact_data = get_all_contacts(sort_by="c.full_name", order="ASC")
        self.contact_dict = {}
        for c in self.contact_data:
            display_name = f"{c[1]} ({c[2]})" if c[2] else c[1]
            self.contact_dict[display_name] = c[0]
        contact_names = ["-- Select Contact --"] + list(self.contact_dict.keys())

        if hasattr(self.parent.master, "all_users"):
             self.user_dict = {user[1]: user[0] for user in self.parent.master.all_users}
        else:
             from core.auth import get_all_users
             self.user_dict = {user[1]: user[0] for user in get_all_users()}
        user_names = ["-- Unassigned --"] + list(self.user_dict.keys())

        # --- MAPEO DE ESTADOS Y PRIORIDADES ---
        self.status_map = {
            "Qualification": "qualification", "Proposal": "proposal", 
            "Evaluation": "evaluation", "Negotiation": "negotiation", 
            "Closed Won": "closed_won", "Closed Lost": "closed_lost"
        }
        self.priority_map = {
            "Very High": "very_high", "High": "high", 
            "Medium": "medium", "Low": "low", "Very Low": "very_low"
        }

        # --- REJILLA PRINCIPAL ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_text = "Edit Opportunity Details" if self.opp_id else "Opportunity Details"
        self.title_label = ctk.CTkLabel(self, text=header_text, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_green)
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, padx=40, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # 1. Nombre
        self.name_entry = self.create_input(self.scroll_frame, "Opportunity Name *", 0)

        # 2. Empresa y Contacto
        self.company_var = ctk.StringVar(value="-- Select Company --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.company_var, values=company_names, fg_color="#3F3F3F", button_color=self.color_green).grid(row=1, column=0, pady=8, sticky="ew")

        self.contact_var = ctk.StringVar(value="-- Select Contact --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.contact_var, values=contact_names, fg_color="#3F3F3F", button_color=self.color_green).grid(row=2, column=0, pady=8, sticky="ew")

        # 3. Estado y Prioridad
        self.status_var = ctk.StringVar(value="Qualification")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.status_var, values=list(self.status_map.keys()), fg_color="#3F3F3F", button_color=self.color_green).grid(row=3, column=0, pady=8, sticky="ew")

        self.priority_var = ctk.StringVar(value="Medium")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.priority_var, values=list(self.priority_map.keys()), fg_color="#3F3F3F", button_color=self.color_green).grid(row=4, column=0, pady=8, sticky="ew")

        # 4. Valor y Fechas
        self.value_entry = self.create_input(self.scroll_frame, "Estimated Value (€)", 5)
        self.proposal_date_entry = self.create_input(self.scroll_frame, "Proposal Deadline (DD/MM/YYYY)", 6)
        self.close_date_entry = self.create_input(self.scroll_frame, "Expected Close Date (DD/MM/YYYY)", 7)

        # 5. Asignado a
        self.assign_var = ctk.StringVar(value="-- Unassigned --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.assign_var, values=user_names, fg_color="#3F3F3F", button_color=self.color_green).grid(row=8, column=0, pady=8, sticky="ew")

        # --- 6. SECCIÓN PRODUCTOS ---
        ctk.CTkLabel(self.scroll_frame, text="Select Products/Services:", font=ctk.CTkFont(weight="bold")).grid(row=9, column=0, pady=(15, 5), sticky="w")
        self.prod_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#2A2A2A")
        self.prod_frame.grid(row=10, column=0, sticky="ew", pady=5)
        
        all_prods = get_all_products()
        for idx, p in enumerate(all_prods):
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(self.prod_frame, text=f"{p[1]} ({p[4]:,.2f}€)", variable=var, text_color="white", fg_color=self.color_green, hover_color="#246B15", border_color=self.color_green)
            cb.pack(anchor="w", padx=10, pady=5)
            self.product_checkboxes[p[0]] = (var, p[4])

        # Botón Guardar
        btn_text = "Update Opportunity" if self.opp_id else "Save Opportunity"
        self.save_btn = ctk.CTkButton(self, text=btn_text, fg_color=self.color_green, hover_color="#246B15", height=40, font=ctk.CTkFont(weight="bold"), command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=20, padx=40, sticky="ew")
        
        if self.opp_id:
            self.populate_data()

    def create_input(self, master, placeholder, row_idx):
        entry = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, border_color=self.color_green)
        entry.grid(row=row_idx, column=0, pady=8, sticky="ew")
        return entry

    def populate_data(self):
        raw_opp = get_opportunity_by_id(self.opp_id)
        if not raw_opp: return
        
        self.name_entry.insert(0, raw_opp[1])
        
        for k, v in self.status_map.items():
            if v == raw_opp[2]: self.status_var.set(k)
        for k, v in self.priority_map.items():
            if v == raw_opp[3]: self.priority_var.set(k)
            
        if raw_opp[5] is not None: self.value_entry.insert(0, str(raw_opp[5]))
        if raw_opp[7]: self.proposal_date_entry.insert(0, raw_opp[7])
        if raw_opp[8]: self.close_date_entry.insert(0, raw_opp[8])
        
        if raw_opp[11]: 
            for k, v in self.company_dict.items():
                if v == raw_opp[11]: self.company_var.set(k)
        if raw_opp[10]: 
            for k, v in self.contact_dict.items():
                if v == raw_opp[10]: self.contact_var.set(k)
        if raw_opp[4]: 
            for k, v in self.user_dict.items():
                if v == raw_opp[4]: self.assign_var.set(k)

        # Marcar checkboxes de productos
        linked = get_opportunity_products(self.opp_id)
        linked_ids = [lp[0] for lp in linked]
        for p_id, (var, price) in self.product_checkboxes.items():
            if p_id in linked_ids:
                var.set(True)

    def save_data(self):
        name = self.name_entry.get()
        if not name.strip():
            self.name_entry.configure(border_color="#A52A2A")
            return
        self.name_entry.configure(border_color=self.color_green)

        val_raw = self.value_entry.get().strip()
        est_value = 0.0
        if val_raw:
            try:
                est_value = float(val_raw.replace(",", "."))
                self.value_entry.configure(border_color=self.color_green)
            except ValueError:
                self.value_entry.configure(border_color="#A52A2A")
                return

        comp_id = self.company_dict.get(self.company_var.get())
        cont_id = self.contact_dict.get(self.contact_var.get())
        user_id = self.user_dict.get(self.assign_var.get())
        
        db_status = self.status_map.get(self.status_var.get(), "qualification")
        db_priority = self.priority_map.get(self.priority_var.get(), "medium")

        # Guardar Oportunidad principal
        if self.opp_id:
            success = update_opportunity(self.opp_id, name, db_status, db_priority, est_value, self.proposal_date_entry.get(), self.close_date_entry.get(), cont_id, comp_id, user_id)
            saved_opp_id = self.opp_id if success else None
        else:
            saved_opp_id = add_opportunity(name, db_status, db_priority, est_value, self.proposal_date_entry.get(), self.close_date_entry.get(), cont_id, comp_id, user_id)

        # Guardar Relación de Productos
        if saved_opp_id:
            unlink_all_products_from_opportunity(saved_opp_id)
            for p_id, (var, price) in self.product_checkboxes.items():
                if var.get():
                    link_product_to_opportunity(saved_opp_id, p_id, quantity=1, price=price)
            
            self.parent.refresh_list()
            self.destroy()
        else:
            show_alert(self, "Database Error", "Could not save the opportunity.")