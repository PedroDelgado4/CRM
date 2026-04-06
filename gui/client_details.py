import customtkinter as ctk
from tkcalendar import DateEntry
from core.contacts import open_email, assign_responsable, add_interaction

class ClientDetailsWindow(ctk.CTkToplevel):
    def __init__(self, master, client_data, all_users):
        super().__init__(master)
        self.title(f"Details: {client_data[1]}")
        self.geometry("500x600")

        # client_data: (id, name, company, email, phone, status, assigned_to)
        self.client_data = client_data
        self.client_id = client_data[0]
        self.all_users = all_users

        # elementos ui
        ctk.CTkLabel(self, text=client_data[1], font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        # email rapido
        mail_frame = ctk.CTkFrame(self, fg_color="transparent")
        mail_frame.pack(pady=5)
        ctk.CTkLabel(mail_frame, text=f"Email: {client_data[3]}").pack(side="left", pady=5)
        ctk.CTkButton(mail_frame, text="Send email...", width=50, command=lambda: open_email(client_data[3])).pack(side="left")
        
        # asignar responasble
        ctk.CTkLabel(self, text="Assign responsable:").pack(pady=(10, 0))

        # mapear ids
        self.user_map = {u[1]: u[0] for u in all_users}
        user_names = list(self.user_map.keys())

        self.user_menu = ctk.CTkOptionMenu(self, values=user_names)
        # por defecto, poner el nombre del responsable actual
        current_resp_name = next((u[1] for u in all_users if u[0] == client_data[6]), "Select...")
        self.user_menu.set(current_resp_name)
        self.user_menu.pack(pady=5)

        # timeline y notas
        ctk.CTkLabel(self, text="Timeline & Notes", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.note_entry = ctk.CTkTextbox(self, height=100)
        self.note_entry.pack(padx=20, pady=5, fill="x")

        # calendario para recrodatorio
        ctk.CTkLabel(self, text="Set reminder date:").pack(pady=(5, 0))
        self.calendar = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.calendar.pack(pady=5)


        ctk.CTkButton(self, text="Add note and save", fg_color="green", command=self.save_and_close).pack(pady=20)
    
    def save_and_close(self):
        # id del resp seleccionado
        selected_user_name = self.user_menu.get()
        user_id = self.user_map.get(selected_user_name)

        # guardar asignacion
        if user_id:
            assign_responsable(self.client_id, user_id)

        # guardar nota
        note_content = self.note_entry.get("1.0", "end-1c").strip()
        if note_content:
            reminder_date = self.calendar.get_date()
            add_interaction(self.client_id, note_content, reminder_date)

        print(f"DEBUG: Saved interaction for client {self.client_id}")
        self.master.refresh_list()
        self.destroy()

        







        

