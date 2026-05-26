import customtkinter as ctk
from datetime import datetime, date
from tkcalendar import DateEntry
from core.interactions import add_interaction, update_interaction, get_interaction_by_id, link_product_to_interaction, unlink_all_products_from_interaction, get_interaction_products
from core.contacts import get_all_contacts
from core.opportunities import get_all_opportunities, update_last_contact_date
from core.products import get_all_products
from gui.alerts import show_alert

class AddInteractionWindow(ctk.CTkToplevel):
    def __init__(self, parent, interaction_id=None):
        super().__init__(parent)
        self.parent = parent
        self.interaction_id = interaction_id
        self.product_checkboxes = {} 
        
        title_text = "Edit Interaction" if self.interaction_id else "Log Interaction"
        self.title(title_text)
        self.geometry("550x850") 
        self.attributes("-topmost", True)
        
        # COLORES NEON NIGHT
        self.configure(fg_color="#050505")
        self.color_neon = "#DEFF9A"
        self.color_error = "#A52A2A"
        self.bg_input = "#0A0A0A"
        self.border_input = "#333333"

        # --- CARGA DE DATOS RELACIONALES ---
        self.contact_data = get_all_contacts(sort_by="c.full_name", order="ASC")
        self.contact_dict = {c[1]: c[0] for c in self.contact_data}
        contact_names = ["-- Select Contact --"] + list(self.contact_dict.keys())

        self.opp_data = get_all_opportunities(sort_by="o.name", order="ASC")
        self.opp_dict = {o[1]: o[0] for o in self.opp_data}
        opp_names = ["-- Select Opportunity (Optional) --"] + list(self.opp_dict.keys())

        self.type_map = {
            "Call": "call", "Email": "email", "Meeting": "meeting", 
            "Message": "message", "Other": "other"
        }
        self.status_map = {
            "Pending": "pending", "Completed": "completed", "Cancelled": "cancelled"
        }

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text=title_text, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_neon)
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, padx=40, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.type_var = ctk.StringVar(value="Call")
        ctk.CTkComboBox(self.scroll_frame, variable=self.type_var, values=list(self.type_map.keys()), fg_color=self.bg_input, border_color=self.border_input, text_color="white", button_color="#223E22", button_hover_color="#bde072", dropdown_fg_color="#151515").grid(row=0, column=0, pady=8, sticky="ew")

        self.contact_var = ctk.StringVar(value="-- Select Contact --")
        ctk.CTkComboBox(self.scroll_frame, variable=self.contact_var, values=contact_names, fg_color=self.bg_input, border_color=self.border_input, text_color="white", button_color="#223E22", button_hover_color="#bde072", dropdown_fg_color="#151515").grid(row=1, column=0, pady=8, sticky="ew")

        self.opp_var = ctk.StringVar(value="-- Select Opportunity (Optional) --")
        ctk.CTkComboBox(self.scroll_frame, variable=self.opp_var, values=opp_names, fg_color=self.bg_input, border_color=self.border_input, text_color="white", button_color="#223E22", button_hover_color="#bde072", dropdown_fg_color="#151515").grid(row=2, column=0, pady=8, sticky="ew")

        ctk.CTkLabel(self.scroll_frame, text="Interaction Notes *", anchor="w", text_color="white").grid(row=3, column=0, pady=(15, 0), sticky="w")
        self.notes_text = ctk.CTkTextbox(self.scroll_frame, height=120, border_width=1, border_color=self.border_input, fg_color=self.bg_input, text_color="white")
        self.notes_text.grid(row=4, column=0, pady=5, sticky="ew")

        self.status_var = ctk.StringVar(value="Completed")
        ctk.CTkComboBox(self.scroll_frame, variable=self.status_var, values=list(self.status_map.keys()), fg_color=self.bg_input, border_color=self.border_input, text_color="white", button_color="#223E22", button_hover_color="#bde072", dropdown_fg_color="#151515").grid(row=5, column=0, pady=8, sticky="ew")

        # FECHA CON TKCALENDAR
        ctk.CTkLabel(self.scroll_frame, text="Follow-up Date:", text_color="white").grid(row=6, column=0, pady=(10,0), sticky="w")
        self.reminder_entry = DateEntry(
            self.scroll_frame, width=20, 
            background=self.bg_input, foreground='white', borderwidth=0,
            selectbackground=self.color_neon, selectforeground='black',
            normalbackground=self.bg_input, normalforeground='white',
            headersbackground='#151515', headersforeground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.reminder_entry.grid(row=7, column=0, pady=(0,8), sticky="w")

        # --- SECCIÓN PRODUCTOS TRATADOS ---
        ctk.CTkLabel(self.scroll_frame, text="Products discussed:", font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=8, column=0, pady=(15, 5), sticky="w")
        self.prod_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#151515", border_width=1, border_color="#333333")
        self.prod_frame.grid(row=9, column=0, sticky="ew", pady=5)
        
        all_prods = get_all_products()
        for idx, p in enumerate(all_prods):
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(self.prod_frame, text=p[1], variable=var, text_color="white", fg_color=self.color_neon, hover_color="#bde072", checkmark_color="black", border_color="#555")
            cb.pack(anchor="w", padx=10, pady=5)
            self.product_checkboxes[p[0]] = var

        btn_text = "Update Interaction" if self.interaction_id else "Save Interaction"
        self.save_btn = ctk.CTkButton(self, text=btn_text, fg_color=self.color_neon, text_color="black", hover_color="#bde072", height=40, font=ctk.CTkFont(weight="bold"), command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=20, padx=40, sticky="ew")
        
        if self.interaction_id:
            self.populate_data()

    def populate_data(self):
        raw_int = get_interaction_by_id(self.interaction_id)
        if not raw_int: return
        
        for k, v in self.type_map.items():
            if v == raw_int[3]: self.type_var.set(k)
            
        for k, v in self.status_map.items():
            if v == raw_int[6]: self.status_var.set(k)
            
        if raw_int[1]: 
            for k, v in self.contact_dict.items():
                if v == raw_int[1]: self.contact_var.set(k)
                
        if raw_int[2]: 
            for k, v in self.opp_dict.items():
                if v == raw_int[2]: self.opp_var.set(k)
                
        if raw_int[4]: self.notes_text.insert("1.0", raw_int[4])
        
        if raw_int[7]:
            try:
                self.reminder_entry.set_date(datetime.strptime(raw_int[7], '%Y-%m-%d').date())
            except ValueError: pass

        linked = get_interaction_products(self.interaction_id)
        linked_ids = [lp[0] for lp in linked]
        for p_id, var in self.product_checkboxes.items():
            if p_id in linked_ids:
                var.set(True)

    def save_data(self):
        notes = self.notes_text.get("1.0", "end-1c").strip()
        if not notes:
            self.notes_text.configure(border_color=self.color_error)
            show_alert(self, "Validation Error", "Interaction Notes are required.")
            return
        self.notes_text.configure(border_color=self.border_input)

        cont_id = self.contact_dict.get(self.contact_var.get())
        if not cont_id:
            show_alert(self, "Validation Error", "You must select a contact before saving.")
            return 
            
        opp_id = self.opp_dict.get(self.opp_var.get()) 
        db_type = self.type_map.get(self.type_var.get(), "call")
        db_status = self.status_map.get(self.status_var.get(), "completed")
        
        reminder = self.reminder_entry.get_date().strftime('%Y-%m-%d')

        if self.interaction_id:
            success = update_interaction(self.interaction_id, cont_id, opp_id, db_type, notes, db_status, reminder)
            saved_id = self.interaction_id if success else None
        else:
            saved_id = add_interaction(contact_id=cont_id, opportunity_id=opp_id, type=db_type, note=notes, status=db_status, reminder_date=reminder)

        if saved_id:
            unlink_all_products_from_interaction(saved_id)
            for p_id, var in self.product_checkboxes.items():
                if var.get(): 
                    link_product_to_interaction(saved_id, p_id)
            
            # --- ÚLTIMO CONTACTO ---
            if opp_id: 
                today_str = date.today().strftime('%Y-%m-%d')
                update_last_contact_date(opp_id, today_str)
            
            self.parent.refresh_list()
            self.destroy()
        else:
            show_alert(self, "Database Error", "Could not save the interaction.")