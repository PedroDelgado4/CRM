import customtkinter as ctk
from datetime import datetime
from tkcalendar import DateEntry
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
        
        # --- COLORES NEON NIGHT ---
        self.configure(fg_color="#050505")
        self.color_neon = "#DEFF9A"
        self.color_error = "#ff4d4d"
        self.bg_input = "#0A0A0A"
        self.border_input = "#333333"
        
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

        header_text = "EDIT OPPORTUNITY" if self.opp_id else "NEW OPPORTUNITY"
        self.title_label = ctk.CTkLabel(self, text=header_text, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_neon)
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, padx=40, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # 1. Nombre
        self.name_entry = self.create_input(self.scroll_frame, "Opportunity Name *", 0)

        # 2. Empresa y Contacto
        self.company_var = ctk.StringVar(value="-- Select Company --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.company_var, values=company_names, fg_color=self.bg_input, button_color=self.color_neon, button_hover_color="#bde072", text_color="white", dropdown_fg_color="#151515").grid(row=1, column=0, pady=8, sticky="ew")

        self.contact_var = ctk.StringVar(value="-- Select Contact --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.contact_var, values=contact_names, fg_color=self.bg_input, button_color=self.color_neon, button_hover_color="#bde072", text_color="white", dropdown_fg_color="#151515").grid(row=2, column=0, pady=8, sticky="ew")

        # 3. Estado y Prioridad
        self.status_var = ctk.StringVar(value="Qualification")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.status_var, values=list(self.status_map.keys()), fg_color=self.bg_input, button_color=self.color_neon, button_hover_color="#bde072", text_color="white", dropdown_fg_color="#151515").grid(row=3, column=0, pady=8, sticky="ew")

        self.priority_var = ctk.StringVar(value="Medium")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.priority_var, values=list(self.priority_map.keys()), fg_color=self.bg_input, button_color=self.color_neon, button_hover_color="#bde072", text_color="white", dropdown_fg_color="#151515").grid(row=4, column=0, pady=8, sticky="ew")

        # 4. Valor y Fechas
        self.value_entry = self.create_input(self.scroll_frame, "Estimated Value (€)", 5)
        
        # FECHAS CON TKCALENDAR
        ctk.CTkLabel(self.scroll_frame, text="Proposal Deadline:", text_color="white").grid(row=6, column=0, pady=(10,0), sticky="w")
        self.proposal_date_entry = DateEntry(
            self.scroll_frame, width=20, 
            background=self.bg_input, foreground='white', borderwidth=0,
            selectbackground=self.color_neon, selectforeground='black',
            normalbackground=self.bg_input, normalforeground='white',
            headersbackground='#151515', headersforeground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.proposal_date_entry.grid(row=7, column=0, pady=(0,8), sticky="w")

        ctk.CTkLabel(self.scroll_frame, text="Expected Close Date:", text_color="white").grid(row=8, column=0, pady=(10,0), sticky="w")
        self.close_date_entry = DateEntry(
            self.scroll_frame, width=20, 
            background=self.bg_input, foreground='white', borderwidth=0,
            selectbackground=self.color_neon, selectforeground='black',
            normalbackground=self.bg_input, normalforeground='white',
            headersbackground='#151515', headersforeground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.close_date_entry.grid(row=9, column=0, pady=(0,8), sticky="w")

        # 5. Asignado a
        self.assign_var = ctk.StringVar(value="-- Unassigned --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.assign_var, values=user_names, fg_color=self.bg_input, button_color=self.color_neon, button_hover_color="#bde072", text_color="white", dropdown_fg_color="#151515").grid(row=10, column=0, pady=8, sticky="ew")

        # --- 6. SECCIÓN PRODUCTOS ---
        ctk.CTkLabel(self.scroll_frame, text="Select Products/Services:", font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=11, column=0, pady=(15, 5), sticky="w")
        self.prod_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#151515", border_width=1, border_color="#333")
        self.prod_frame.grid(row=12, column=0, sticky="ew", pady=5)
        
        all_prods = get_all_products()
        for idx, p in enumerate(all_prods):
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(self.prod_frame, text=f"{p[1]} ({p[4]:,.2f}€)", variable=var, text_color="white", fg_color=self.color_neon, checkmark_color="black", hover_color="#bde072", border_color="#555")
            cb.pack(anchor="w", padx=10, pady=10)
            self.product_checkboxes[p[0]] = (var, p[4])

        # Botón Guardar
        btn_text = "UPDATE OPPORTUNITY" if self.opp_id else "SAVE OPPORTUNITY"
        self.save_btn = ctk.CTkButton(self, text=btn_text, fg_color=self.color_neon, text_color="black", hover_color="#bde072", height=40, font=ctk.CTkFont(weight="bold"), command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=20, padx=40, sticky="ew")
        
        if self.opp_id:
            self.populate_data()

    def create_input(self, master, placeholder, row_idx):
        entry = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, fg_color=self.bg_input, border_color=self.border_input, text_color="white")
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
        
        if raw_opp[7]: 
            try:
                self.proposal_date_entry.set_date(datetime.strptime(raw_opp[7], '%Y-%m-%d').date())
            except ValueError: pass
            
        if raw_opp[8]: 
            try:
                self.close_date_entry.set_date(datetime.strptime(raw_opp[8], '%Y-%m-%d').date())
            except ValueError: pass
        
        if raw_opp[11]: 
            for k, v in self.company_dict.items():
                if v == raw_opp[11]: self.company_var.set(k)
        if raw_opp[10]: 
            for k, v in self.contact_dict.items():
                if v == raw_opp[10]: self.contact_var.set(k)
        if raw_opp[4]: 
            for k, v in self.user_dict.items():
                if v == raw_opp[4]: self.assign_var.set(k)

        linked = get_opportunity_products(self.opp_id)
        linked_ids = [lp[0] for lp in linked]
        for p_id, (var, price) in self.product_checkboxes.items():
            if p_id in linked_ids:
                var.set(True)

    def save_data(self):
        name = self.name_entry.get()
        if not name.strip():
            self.name_entry.configure(border_color=self.color_error)
            return
        self.name_entry.configure(border_color=self.border_input)

        val_raw = self.value_entry.get().strip()
        est_value = 0.0
        if val_raw:
            try:
                est_value = float(val_raw.replace(",", "."))
                self.value_entry.configure(border_color=self.border_input)
            except ValueError:
                self.value_entry.configure(border_color=self.color_error)
                return

        comp_id = self.company_dict.get(self.company_var.get())
        cont_id = self.contact_dict.get(self.contact_var.get())
        user_id = self.user_dict.get(self.assign_var.get())
        
        db_status = self.status_map.get(self.status_var.get(), "qualification")
        db_priority = self.priority_map.get(self.priority_var.get(), "medium")

        proposal_date = self.proposal_date_entry.get_date().strftime('%Y-%m-%d')
        close_date = self.close_date_entry.get_date().strftime('%Y-%m-%d')

        if self.opp_id:
            success = update_opportunity(self.opp_id, name, db_status, db_priority, est_value, proposal_date, close_date, cont_id, comp_id, user_id)
            saved_opp_id = self.opp_id if success else None
        else:
            saved_opp_id = add_opportunity(name, db_status, db_priority, est_value, proposal_date, close_date, cont_id, comp_id, user_id)

        if saved_opp_id:
            unlink_all_products_from_opportunity(saved_opp_id)
            for p_id, (var, price) in self.product_checkboxes.items():
                if var.get():
                    link_product_to_opportunity(saved_opp_id, p_id, quantity=1, price=price)
            
            self.parent.refresh_list()
            self.destroy()
        else:
            show_alert(self, "Database Error", "Could not save the opportunity.")