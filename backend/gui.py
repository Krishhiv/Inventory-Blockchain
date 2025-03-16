import tkinter as tk
from tkinter import ttk, messagebox
from blockchain import Blockchain  # Import your Blockchain class

# Initialize the blockchain
luxury_inventory = Blockchain()

class BlockchainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Luxury Inventory Blockchain")
        self.root.geometry("800x600")

        # Title
        tk.Label(root, text="Luxury Goods Blockchain", font=("Arial", 16, "bold")).pack(pady=10)

        # Frame for adding items
        self.add_frame = tk.LabelFrame(root, text="Add New Item", padx=10, pady=10)
        self.add_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(self.add_frame, text="UID:").grid(row=0, column=0, padx=5, pady=5)
        self.uid_entry = tk.Entry(self.add_frame)
        self.uid_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.add_frame, text="Brand:").grid(row=1, column=0, padx=5, pady=5)
        self.brand_entry = tk.Entry(self.add_frame)
        self.brand_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.add_frame, text="Item Name:").grid(row=2, column=0, padx=5, pady=5)
        self.item_entry = tk.Entry(self.add_frame)
        self.item_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.add_frame, text="Price (₹):").grid(row=3, column=0, padx=5, pady=5)
        self.price_entry = tk.Entry(self.add_frame)
        self.price_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(self.add_frame, text="Add Item", command=self.add_item).grid(row=4, column=0, columnspan=2, pady=10)

        # Frame for executing sales
        self.sale_frame = tk.LabelFrame(root, text="Execute Sale", padx=10, pady=10)
        self.sale_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(self.sale_frame, text="UID:").grid(row=0, column=0, padx=5, pady=5)
        self.sale_uid_entry = tk.Entry(self.sale_frame)
        self.sale_uid_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.sale_frame, text="Customer Name:").grid(row=1, column=0, padx=5, pady=5)
        self.customer_entry = tk.Entry(self.sale_frame)
        self.customer_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.sale_frame, text="Execute Sale", command=self.execute_sale).grid(row=2, column=0, columnspan=2, pady=10)

        # Validate Chain Button
        tk.Button(root, text="Validate Blockchain", command=self.validate_chain).pack(pady=10)

        # Blockchain Display
        self.display_frame = tk.LabelFrame(root, text="Blockchain State", padx=10, pady=10)
        self.display_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(self.display_frame, columns=("UID", "Brand", "Item", "Price", "Status", "Date", "PrevHash", "Hash"), show="headings")
        self.tree.heading("UID", text="UID")
        self.tree.heading("Brand", text="Brand")
        self.tree.heading("Item", text="Item Name")
        self.tree.heading("Price", text="Price (₹)")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Date", text="Date")
        self.tree.heading("PrevHash", text="Prev Hash")
        self.tree.heading("Hash", text="Hash")
        self.tree.column("UID", width=50)
        self.tree.column("Brand", width=100)
        self.tree.column("Item", width=150)
        self.tree.column("Price", width=80)
        self.tree.column("Status", width=80)
        self.tree.column("Date", width=80)
        self.tree.column("PrevHash", width=100)
        self.tree.column("Hash", width=100)
        self.tree.pack(fill="both", expand=True)

        # Initial blockchain display
        self.update_display()

    def add_item(self):
        try:
            uid = int(self.uid_entry.get())
            brand = self.brand_entry.get()
            item_name = self.item_entry.get()
            price = float(self.price_entry.get())

            if not brand or not item_name:
                raise ValueError("Brand and Item Name cannot be empty!")

            luxury_inventory.add_block(uid, brand, item_name, price)
            self.update_display()
            messagebox.showinfo("Success", f"Item {brand} {item_name} added to blockchain!")
            self.clear_add_entries()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def execute_sale(self):
        try:
            uid = int(self.sale_uid_entry.get())
            customer_name = self.customer_entry.get()

            if not customer_name:
                raise ValueError("Customer Name cannot be empty!")

            success = luxury_inventory.execute_sale(uid, customer_name)
            if success:
                self.update_display()
                messagebox.showinfo("Success", f"Sale executed for UID {uid} to {customer_name}!")
            else:
                messagebox.showerror("Error", f"Sale failed for UID {uid}. Item may not exist or is already sold.")
            self.clear_sale_entries()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def validate_chain(self):
        if luxury_inventory.validate_chain():
            messagebox.showinfo("Validation", "Blockchain is valid and secure!")
        else:
            messagebox.showerror("Validation", "Blockchain integrity compromised!")

    def update_display(self):
        # Clear current display
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Traverse and display blockchain
        current = luxury_inventory.head
        while current:
            self.tree.insert("", "end", values=(
                current.uid, 
                current.brand, 
                current.item_name, 
                current.price, 
                current.status, 
                current.timestamp, 
                current.prevHash[:8] + "...",  # Shorten for readability
                current.hash[:8] + "..."       # Shorten for readability
            ))
            current = current.next

    def clear_add_entries(self):
        self.uid_entry.delete(0, tk.END)
        self.brand_entry.delete(0, tk.END)
        self.item_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

    def clear_sale_entries(self):
        self.sale_uid_entry.delete(0, tk.END)
        self.customer_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = BlockchainGUI(root)
    root.mainloop()