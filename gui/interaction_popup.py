import customtkinter as ctk
from core.interactions import add_interaction
from core.contacts import get_all_contacts
from core.opportunities import get_all_opportunities
from gui.alerts import show_alert

class AddInteractionWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Log Interaction")
        self.geometry("500x650")
        self.attributes("-topmost", True)
        
        self.color_green = "#2E8D1B"

        # --- CARGA DE DATOS RELACIONALES ---
        # 1. Contactos 
        self.contact_data = get_all_contacts(sort_by="c.full_name", order="ASC")
        self.contact_dict = {c[1]: c[0] for c in self.contact_data}
        contact_names = ["-- Select Contact --"] + list(self.contact_dict.keys())

        # 2. Oportunidades (Opcional, puede ser una llamada general)
        self.opp_data = get_all_opportunities(sort_by="o.name", order="ASC")
        self.opp_dict = {o[1]: o[0] for o in self.opp_data}
        opp_names = ["-- Select Opportunity (Optional) --"] + list(self.opp_dict.keys())

        # --- MAPEO DE TIPOS Y ESTADOS ---
        self.type_map = {
            "Call": "call",
            "Email": "email",
            "Meeting": "meeting",
            "Message": "message",
            "Other": "other"
        }
        self.status_map = {
            "Pending": "pending",
            "Completed": "completed",
            "Cancelled": "cancelled"
        }

        # --- REJILLA PRINCIPAL ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Log Interaction", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_green)
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        # Contenedor Scrollable
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, padx=40, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # 1. Tipo de Interacción
        self.type_var = ctk.StringVar(value="Call")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.type_var, values=list(self.type_map.keys()), fg_color="#3F3F3F", button_color=self.color_green).grid(row=0, column=0, pady=8, sticky="ew")

        # 2. Relaciones
        self.contact_var = ctk.StringVar(value="-- Select Contact --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.contact_var, values=contact_names, fg_color="#3F3F3F", button_color=self.color_green).grid(row=1, column=0, pady=8, sticky="ew")

        self.opp_var = ctk.StringVar(value="-- Select Opportunity (Optional) --")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.opp_var, values=opp_names, fg_color="#3F3F3F", button_color=self.color_green).grid(row=2, column=0, pady=8, sticky="ew")

        # 3. Notas 
        ctk.CTkLabel(self.scroll_frame, text="Interaction Notes *", anchor="w").grid(row=3, column=0, pady=(15, 0), sticky="w")
        self.notes_text = ctk.CTkTextbox(self.scroll_frame, height=120, border_width=2, border_color=self.color_green)
        self.notes_text.grid(row=4, column=0, pady=5, sticky="ew")

        # 4. Estado
        self.status_var = ctk.StringVar(value="Completed")
        ctk.CTkOptionMenu(self.scroll_frame, variable=self.status_var, values=list(self.status_map.keys()), fg_color="#3F3F3F", button_color=self.color_green).grid(row=5, column=0, pady=8, sticky="ew")

        # 5. Fecha de Recordatorio (Opcional, texto temporalmente)
        self.reminder_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Follow-up Date (DD/MM/YYYY)", height=35, border_color=self.color_green)
        self.reminder_entry.grid(row=6, column=0, pady=(15, 8), sticky="ew")

        # Botón Guardar
        self.save_btn = ctk.CTkButton(self, text="Save Interaction", fg_color=self.color_green, hover_color="#246B15", height=40, font=ctk.CTkFont(weight="bold"), command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=20, padx=40, sticky="ew")

    def save_data(self):
        # 1. Validar Notas (Mínimo requerido para saber de qué se habló)
        notes = self.notes_text.get("1.0", "end-1c").strip()
        if not notes:
            self.notes_text.configure(border_color="#A52A2A")
            return
        self.notes_text.configure(border_color=self.color_green)

        # 2. Obtener IDs (Validar que se eligió un contacto)
        cont_id = self.contact_dict.get(self.contact_var.get())
        if not cont_id:
            show_alert(self, "Validation Error", "You must select a contact before saving.")
            return 
            
        opp_id = self.opp_dict.get(self.opp_var.get()) # Esto puede ser None, y es correcto.

        # 3. Mapear Desplegables
        db_type = self.type_map.get(self.type_var.get(), "call")
        db_status = self.status_map.get(self.status_var.get(), "completed")

        # 4. Guardar
        success = add_interaction(
            contact_id=cont_id,
            opportunity_id=opp_id,
            interaction_type=db_type,
            note=notes,
            status=db_status,
            reminder_date=self.reminder_entry.get()
        )

        if success:
            self.parent.refresh_list()
            self.destroy()