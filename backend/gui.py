import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import time
from blockchain import Blockchain, Block
from ttkthemes import ThemedTk
import customtkinter as ctk
import getpass

class PasswordDialog:
    def __init__(self, parent, title, role_required=False):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.result = None
        
        # Center the dialog
        self.center_window()
        
        # Create form
        ctk.CTkLabel(self.dialog, text=title, font=("Helvetica", 16, "bold")).pack(pady=20)
        
        # Name field
        ctk.CTkLabel(self.dialog, text="Name:").pack(pady=5)
        self.name_entry = ctk.CTkEntry(self.dialog, width=200)
        self.name_entry.pack(pady=5)
        
        # Role field (if required)
        if role_required:
            ctk.CTkLabel(self.dialog, text="Role:").pack(pady=5)
            self.role_var = tk.StringVar(value="employee")
            self.role_frame = ctk.CTkFrame(self.dialog)
            self.role_frame.pack(pady=5)
            ctk.CTkRadioButton(self.role_frame, text="Employee", variable=self.role_var, 
                             value="employee").pack(side="left", padx=10)
            ctk.CTkRadioButton(self.role_frame, text="Customer", variable=self.role_var, 
                             value="customer").pack(side="left", padx=10)
        
        # Password field
        ctk.CTkLabel(self.dialog, text="Password:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.dialog, show="*", width=200)
        self.password_entry.pack(pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Submit", command=self.submit).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel).pack(side="left", padx=10)

    def center_window(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'+{x}+{y}')

    def submit(self):
        if not self.name_entry.get() or not self.password_entry.get():
            messagebox.showerror("Error", "Please fill in all fields")
            return
        if hasattr(self, 'role_var'):
            self.result = (self.name_entry.get(), self.role_var.get(), self.password_entry.get())
        else:
            self.result = (self.name_entry.get(), self.password_entry.get())
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()

class BlockchainGUI:
    def __init__(self):
        # Initialize blockchain
        self.blockchain = Blockchain()
        
        # Create themed root window
        self.root = ctk.CTk()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root.title("Blockchain Inventory System")
        self.root.geometry("1400x800")
        
        # Create main container
        self.create_layout()
        
        # Start periodic refresh
        self.start_periodic_refresh()

    def create_layout(self):
        # Create main frames
        self.sidebar = ctk.CTkFrame(self.root, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Sidebar content
        self.create_sidebar()
        
        # Main content
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()

    def create_sidebar(self):
        # Title
        ctk.CTkLabel(self.sidebar, text="Control Panel", 
                    font=("Helvetica", 16, "bold")).pack(pady=20)
        
        # Buttons
        buttons = [
            ("Add Item", self.show_add_item_dialog),
            ("Execute Sale", self.show_sale_dialog),
            ("Verify Chain", self.verify_chain),
            ("View Merkle Tree", self.show_merkle_tree),
            ("Register User", self.show_register_dialog)
        ]
        
        for text, command in buttons:
            ctk.CTkButton(self.sidebar, text=text, command=command).pack(pady=10, padx=20, fill="x")

    def create_main_content(self):
        # Create tabview
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True)
        
        # Blockchain tab
        blockchain_tab = self.tabview.add("Blockchain")
        
        # Create treeview with scrollbar
        tree_frame = ctk.CTkFrame(blockchain_tab)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create Treeview
        style = ttk.Style()
        style.configure("Treeview", background="#2a2d2e", 
                       fieldbackground="#2a2d2e", foreground="white")
        
        self.tree = ttk.Treeview(tree_frame, columns=("UID", "Brand", "Item", "Price", "Status", "Date", "Signatures"))
        
        # Configure columns
        self.tree.heading("UID", text="UID")
        self.tree.heading("Brand", text="Brand")
        self.tree.heading("Item", text="Item Name")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Date", text="Date Added")
        self.tree.heading("Signatures", text="Signatures")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_status_bar(self):
        self.status_var = tk.StringVar(value="System Ready")
        self.status_bar = ctk.CTkLabel(self.root, textvariable=self.status_var)
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)

    def show_add_item_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Item")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'+{x}+{y}')

        # Create main form
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(main_frame, text="Add New Item", 
                    font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Create form fields
        fields_frame = ctk.CTkFrame(main_frame)
        fields_frame.pack(fill="x", pady=10)
        
        entries = {}
        
        # Item details
        ctk.CTkLabel(fields_frame, text="UID:").pack(pady=5)
        entries["uid"] = ctk.CTkEntry(fields_frame)
        entries["uid"].pack(pady=5)
        
        ctk.CTkLabel(fields_frame, text="Brand:").pack(pady=5)
        entries["brand"] = ctk.CTkEntry(fields_frame)
        entries["brand"].pack(pady=5)
        
        ctk.CTkLabel(fields_frame, text="Item Name:").pack(pady=5)
        entries["item_name"] = ctk.CTkEntry(fields_frame)
        entries["item_name"].pack(pady=5)
        
        ctk.CTkLabel(fields_frame, text="Price:").pack(pady=5)
        entries["price"] = ctk.CTkEntry(fields_frame)
        entries["price"].pack(pady=5)
        
        ctk.CTkLabel(fields_frame, text="Status:").pack(pady=5)
        entries["status"] = ctk.CTkComboBox(fields_frame, values=["Available", "Reserved"])
        entries["status"].pack(pady=5)
        
        # Employee credentials
        cred_frame = ctk.CTkFrame(main_frame)
        cred_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(cred_frame, text="Employee Name:").pack(pady=5)
        entries["emp_name"] = ctk.CTkEntry(cred_frame)
        entries["emp_name"].pack(pady=5)
        
        ctk.CTkLabel(cred_frame, text="Password:").pack(pady=5)
        entries["emp_password"] = ctk.CTkEntry(cred_frame, show="*")
        entries["emp_password"].pack(pady=5)

        def submit():
            try:
                # Validate and get values
                uid = int(entries["uid"].get())
                brand = entries["brand"].get()
                item_name = entries["item_name"].get()
                price = float(entries["price"].get())
                status = entries["status"].get()
                emp_name = entries["emp_name"].get()
                emp_password = entries["emp_password"].get()
                
                # Validate all fields are filled
                if not all([brand, item_name, emp_name, emp_password]):
                    messagebox.showerror("Error", "Please fill in all fields")
                    return
                
                # Add block with credentials
                success = self.blockchain.add_block(
                    uid, brand, item_name, price, status,
                    credentials=(emp_name, emp_password)
                )
                
                if success:
                    # Wait for verification
                    time.sleep(2)
                    # Refresh display
                    self.refresh_blockchain_display()
                    # Show success message
                    messagebox.showinfo("Success", f"Added new item: {brand} - {item_name}")
                    # Close dialog
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to add block. Check credentials and try again.")
                
            except ValueError as e:
                messagebox.showerror("Error", "Please enter valid numeric values for UID and Price")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Submit", command=submit).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Cancel", 
                     command=dialog.destroy).pack(side="left", padx=10)

    def show_sale_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Execute Sale")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'+{x}+{y}')
        
        ctk.CTkLabel(dialog, text="Execute Sale", 
                    font=("Helvetica", 16, "bold")).pack(pady=20)
        
        # Create form fields
        fields = [("UID", "entry"), ("Brand", "entry")]
        entries = {}
        
        for field in fields:
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(frame, text=f"{field[0]}:").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame, width=200)
            entry.pack(side="right", padx=5)
            entries[field[0]] = entry

        def submit():
            try:
                uid = int(entries["UID"].get())
                brand = entries["Brand"].get()
                
                self.blockchain.execute_sale(uid, brand)
                dialog.destroy()
                # Schedule a delayed refresh and message
                self.root.after(2000, lambda: self.post_sale_actions(uid))
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid UID")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Execute Sale", 
                     command=submit).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Cancel", 
                     command=dialog.destroy).pack(side="left", padx=10)

    def post_sale_actions(self, uid):
        """Actions to perform after sale execution"""
        self.refresh_blockchain_display()
        messagebox.showinfo("Success", f"Sale executed for item UID: {uid}")
        self.status_var.set(f"Sale executed for item UID: {uid}")

    def refresh_blockchain_display(self):
        """Refresh the blockchain display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add blocks from each chain (excluding genesis blocks)
        for letter in sorted(self.blockchain.chains.keys()):
            current = self.blockchain.chains[letter]
            while current:
                if current.uid != 0:  # Skip genesis blocks
                    signatures = []
                    if current.creation_signature:
                        signatures.append("Creation ✓")
                    if current.sale_agg_signature:
                        signatures.append("Sale ✓")
                    
                    self.tree.insert("", "end", values=(
                        current.uid,
                        current.brand,
                        current.item_name,
                        f"₹{current.price}",
                        current.status,
                        current.timestamp,
                        ", ".join(signatures) if signatures else "None"
                    ))
                current = current.next
        
        # Force update
        self.tree.update()
        self.root.update()

    def verify_chain(self):
        result = self.blockchain.validate_chain()
        if result:
            messagebox.showinfo("Verification", "Blockchain integrity verified successfully!")
            self.status_var.set("Chain verification: Success")
        else:
            messagebox.showerror("Verification", "Blockchain integrity verification failed!")
            self.status_var.set("Chain verification: Failed")

    def show_merkle_tree(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Merkle Tree View")
        dialog.geometry("600x400")
        
        # Add text widget to display Merkle tree
        text_widget = ctk.CTkTextbox(dialog, width=580, height=350)
        text_widget.pack(padx=10, pady=10)
        
        # Redirect print output to the text widget
        import sys
        from io import StringIO
        
        # Capture the output
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result
        
        # Print the Merkle tree
        self.blockchain.print_merkle_tree()
        
        # Restore stdout and get the captured output
        sys.stdout = old_stdout
        text_widget.insert("1.0", result.getvalue())
        text_widget.configure(state="disabled")

    def show_register_dialog(self):
        pwd_dialog = PasswordDialog(self.root, "Register New User", role_required=True)
        self.root.wait_window(pwd_dialog.dialog)
        
        if pwd_dialog.result:
            name, role, password = pwd_dialog.result
            try:
                from signatures import Keys
                user = Keys(name, role, password)
                user.add_to_json()
                messagebox.showinfo("Success", f"{role.capitalize()} '{name}' successfully registered!")
                self.status_var.set(f"New {role} registered: {name}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def periodic_refresh(self):
        """Periodic refresh function"""
        self.refresh_blockchain_display()
        self.root.after(2000, self.periodic_refresh)

    def start_periodic_refresh(self):
        """Start periodic refresh of blockchain display"""
        self.root.after(2000, self.periodic_refresh)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BlockchainGUI()
    app.run()