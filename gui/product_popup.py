import customtkinter as ctk
from core.products import add_product

class AddProductWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent) 
        self.parent = parent
        self.title("Register new product")
        self.geometry("450x650")
        self.attributes("-topmost", True)

        self.color_green = "#2E8D1B"
        
        # Opciones para los despligables

        self.categories = ["-- Select Category --", "Servicio", "Curso"]
        self.billing_models = ["-- Select Billing Model --", "Single payment", "Suscription", "Semestral", "Anual"]

        # rejilla principal
        self.grid_columnconfigure(0, weight=1)
        #titulo
        self.title_label = ctk.CTkLabel(self, text="Product Details", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_green)
        self.title_label.grid(row=0, column=0, pady=(20,10), sticky="ew")

        #formualrio
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx=40, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)

        #nombre
        self.name_entry = self.create_input(self.form_frame, "Product Name *", 0)

        # descripcion
        self.desc_entry = self.create_input(self.form_frame, "Short description", 1)

        # categoria
        self.category_var = ctk.StringVar(value="-- Select category --")
        self.category_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.category_var, values=self.categories,
                                               fg_color="#3F3F3F", button_color=self.color_green, button_hover_color="#246B15")
        self.category_menu.grid(row=2, column=0, pady=8, sticky="ew")

        # precio minimo
        self.price_entry = self.create_input(self.form_frame, "Minimum Price (€)", 3)

        #modelo de facturacion (desplegable)
        self.billing_var = ctk.StringVar(value="-- Select Billing Model --")
        self.billing_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.billing_var, values=self.billing_models,
                                              fg_color="#3F3F3F", button_color=self.color_green, button_hover_color="#246B15")
        self.billing_menu.grid(row=4, column=0, pady=8, sticky="ew")

        #url
        self.url_entry = self.create_input(self.form_frame, "Dossier / Web URL", 5)

        # estado (switch) activo/inactivo
        self.status_var = ctk.StringVar(value="Active")
        self.status_switch = ctk.CTkSwitch(self.form_frame, text="Product is ACTIVE", command=self.toggle_status, onvalue="Active", offvalue="Inactive",
                                           progress_color=self.color_green)
        self.status_switch.select()
        self.status_switch.grid(row=6, column=0, pady=15, sticky="w")

        self.save_btn = ctk.CTkButton(self, text="Save product", fg_color=self.color_green, hover_color="#246B15",
                                      height=40, font=ctk.CTkFont(weight="bold"), command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=25, padx=40, sticky="ew")

    def create_input(self,master, placeholder, row_idx):
        entry = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, border_color=self.color_green)
        entry.grid(row=row_idx, column=0, pady=8, sticky="ew")
        return entry

    def toggle_status(self):
        # actualiza el texto del switch segun estado
        if self.status_var.get() == "Active":
            self.status_switch.configure(text="Product is ACTIVE")
        else:
            self.status_switch.configure(text="Product is INACTIVE")

    def save_data(self):
        # validacion de nombre
        name = self.name_entry.get()
        if not name or name.strip() == "":
            self.name_entry.configure(border_color="#A52A2A")
            return
        self.name_entry.configure(border_color=self.color_green)

        # validacion de precio
        price_raw = self.price_entry.get()
        min_price = 0.0
        if price_raw.strip():
            try:
                min_price = float(price_raw.replace(",", ".")) # cambia comas por puntos
                self.price_entry.configure(border_color=self.color_green)
            except ValueError:
                self.price_entry.configure(border_color="#A52A2A") # Rojo si meten letras
                return

        # procesar valores de los desplegables
        category = self.category_var.get()
        if category == "-- Select category --": category = ""
        
        billing = self.billing_var.get()
        if billing == "-- Select Billing Model --": billing = ""

        # guardar en DB
        success = add_product(
            name=name, 
            description=self.desc_entry.get(), 
            category=category, 
            min_price=min_price, 
            billing_model=billing, 
            status=self.status_var.get(), 
            product_url=self.url_entry.get())
        if success:
            self.parent.refresh_list()
            self.destroy()
            





                                          





