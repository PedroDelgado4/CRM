import customtkinter as ctk
from core.products import add_product, update_product
from gui.alerts import show_alert

class AddProductWindow(ctk.CTkToplevel):
    def __init__(self, parent, product_data=None):
        super().__init__(parent) 
        self.parent = parent
        self.product_data = product_data
        self.product_id = product_data[0] if product_data else None
        
        title_text = "Edit Product" if self.product_id else "Register new product"
        self.title(title_text)
        self.geometry("450x650")
        self.attributes("-topmost", True)

        self.color_green = "#2E8D1B"
        
        self.categories = ["-- Select Category --", "Servicio", "Curso"]
        self.billing_models = ["-- Select Billing Model --", "Single payment", "Suscription", "Semestral", "Anual"]

        self.grid_columnconfigure(0, weight=1)
        
        header_text = "Edit Product Details" if self.product_id else "Product Details"
        self.title_label = ctk.CTkLabel(self, text=header_text, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_green)
        self.title_label.grid(row=0, column=0, pady=(20,10), sticky="ew")

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx=40, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)

        self.name_entry = self.create_input(self.form_frame, "Product Name *", 0)
        self.desc_entry = self.create_input(self.form_frame, "Short description", 1)

        self.category_var = ctk.StringVar(value="-- Select category --")
        self.category_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.category_var, values=self.categories,
                                               fg_color="#3F3F3F", button_color=self.color_green, button_hover_color="#246B15")
        self.category_menu.grid(row=2, column=0, pady=8, sticky="ew")

        self.price_entry = self.create_input(self.form_frame, "Minimum Price (€)", 3)

        self.billing_var = ctk.StringVar(value="-- Select Billing Model --")
        self.billing_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.billing_var, values=self.billing_models,
                                              fg_color="#3F3F3F", button_color=self.color_green, button_hover_color="#246B15")
        self.billing_menu.grid(row=4, column=0, pady=8, sticky="ew")

        self.url_entry = self.create_input(self.form_frame, "Dossier / Web URL", 5)

        self.status_var = ctk.StringVar(value="Active")

        self.status_switch = ctk.CTkSwitch(self.form_frame, text="Product is ACTIVE", variable=self.status_var, command=self.toggle_status, onvalue="Active", offvalue="Inactive",
                                           progress_color=self.color_green)
        self.status_switch.select()
        self.status_switch.grid(row=6, column=0, pady=15, sticky="w")

        btn_text = "Update product" if self.product_id else "Save product"
        self.save_btn = ctk.CTkButton(self, text=btn_text, fg_color=self.color_green, hover_color="#246B15",
                                      height=40, font=ctk.CTkFont(weight="bold"), command=self.save_data)
        self.save_btn.grid(row=2, column=0, pady=25, padx=40, sticky="ew")
        
        # Si estamos editando, rellenamos los campos
        if self.product_data:
            self.populate_data()

    def create_input(self, master, placeholder, row_idx):
        entry = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, border_color=self.color_green)
        entry.grid(row=row_idx, column=0, pady=8, sticky="ew")
        return entry

    def toggle_status(self):
        if self.status_var.get() == "Active":
            self.status_switch.configure(text="Product is ACTIVE")
        else:
            self.status_switch.configure(text="Product is INACTIVE")

    def populate_data(self):
        # id(0), name(1), desc(2), cat(3), price(4), billing(5), status(6), url(7)
        self.name_entry.insert(0, self.product_data[1])
        if self.product_data[2]: self.desc_entry.insert(0, self.product_data[2])
        if self.product_data[3]: self.category_var.set(self.product_data[3])
        if self.product_data[4] is not None: self.price_entry.insert(0, str(self.product_data[4]))
        if self.product_data[5]: self.billing_var.set(self.product_data[5])
        
        self.status_var.set(self.product_data[6] if self.product_data[6] else "Active")
        if self.status_var.get() == "Active": self.status_switch.select()
        else: self.status_switch.deselect()
        self.toggle_status()
        
        if self.product_data[7]: self.url_entry.insert(0, self.product_data[7])

    def save_data(self):
        name = self.name_entry.get()
        if not name or name.strip() == "":
            self.name_entry.configure(border_color="#A52A2A")
            show_alert(self, "Validation Error", "You must enter a name before saving.")
            return
        self.name_entry.configure(border_color=self.color_green)

        price_raw = self.price_entry.get()
        min_price = 0.0
        if price_raw.strip():
            try:
                min_price = float(price_raw.replace(",", "."))
                self.price_entry.configure(border_color=self.color_green)
            except ValueError:
                self.price_entry.configure(border_color="#A52A2A")
                show_alert(self, "Validation Error", "Price must be a valid number.")
                return

        category = self.category_var.get()
        if category == "-- Select category --": category = ""
        
        billing = self.billing_var.get()
        if billing == "-- Select Billing Model --": billing = ""

        # Dependiendo de si existe el ID, añadimos o actualizamos
        if self.product_id:
            success = update_product(self.product_id, name, self.desc_entry.get(), category, min_price, billing, self.status_var.get(), self.url_entry.get())
        else:
            success = add_product(name, self.desc_entry.get(), category, min_price, billing, self.status_var.get(), self.url_entry.get())
            
        if success:
            self.parent.refresh_list()
            self.destroy()
            





                                          





