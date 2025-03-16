import time
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox

class Block:
    def __init__(self, uid, brand, item_name, price, prevHash=""):
        self.uid = uid
        self.brand = brand
        self.item_name = item_name
        self.price = price
        self.timestamp = time.strftime("%d-%m-%Y")
        self.prevHash = prevHash
        self.hash = self.calculate_hash()
        self.next = None

    def calculate_hash(self):
        block_data = (
            str(self.uid) + self.brand + self.item_name + str(self.price) +
            str(self.timestamp) + self.prevHash
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.head = self.create_genesis_block()
        self.tail = self.head

    def create_genesis_block(self):
        return Block(uid=0, brand="Genesis", item_name="Genesis Block", price=0)

    def add_block(self, uid, brand, item_name, price):
        new_block = Block(uid, brand, item_name, price, prevHash=self.tail.hash)
        self.tail.next = new_block
        self.tail = new_block
        return True

    def validate_chain(self):
        ptr = self.head
        while ptr.next:
            block_data = (
                str(ptr.uid) + ptr.brand + ptr.item_name + str(ptr.price) +
                str(ptr.timestamp) + ptr.prevHash
            )
            recalculated_hash = hashlib.sha256(block_data.encode()).hexdigest()

            if recalculated_hash != ptr.hash or ptr.next.prevHash != ptr.hash:
                return False
            ptr = ptr.next
        return True

class BlockchainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Luxury Retail Blockchain")
        self.root.geometry("800x600")
        
        self.blockchain = Blockchain()
        self.next_uid = 1
        
        # Initial test data
        self.blockchain.add_block(1, "Rolex", "Daytona", 300000)
        self.blockchain.add_block(2, "Louis Vuitton", "Leather Handbag", 250000)
        self.blockchain.add_block(3, "Ferrari", "SF90 Stradale", 55000000)
        self.next_uid = 4

        self.create_widgets()

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill="x")

        ttk.Label(input_frame, text="Brand:").grid(row=0, column=0, padx=5, pady=5)
        self.brand_entry = ttk.Entry(input_frame)
        self.brand_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Item Name:").grid(row=0, column=2, padx=5, pady=5)
        self.item_entry = ttk.Entry(input_frame)
        self.item_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Price (₹):").grid(row=0, column=4, padx=5, pady=5)
        self.price_entry = ttk.Entry(input_frame)
        self.price_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(input_frame, text="Add Item", command=self.add_item).grid(row=0, column=6, padx=5, pady=5)

        # Blockchain Display
        display_frame = ttk.Frame(self.root, padding="10")
        display_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(display_frame, columns=("UID", "Brand", "Item", "Price", "Date", "Hash"), show="headings")
        self.tree.heading("UID", text="UID")
        self.tree.heading("Brand", text="Brand")
        self.tree.heading("Item", text="Item Name")
        self.tree.heading("Price", text="Price (₹)")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Hash", text="Hash")
        
        self.tree.column("UID", width=50)
        self.tree.column("Brand", width=100)
        self.tree.column("Item", width=150)
        self.tree.column("Price", width=80)
        self.tree.column("Date", width=80)
        self.tree.column("Hash", width=200)

        self.tree.pack(fill="both", expand=True)

        # Control Buttons
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill="x")

        ttk.Button(control_frame, text="Refresh", command=self.refresh_display).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Validate Chain", command=self.validate_chain).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Exit", command=self.root.quit).pack(side="right", padx=5)

        self.refresh_display()

    def add_item(self):
        try:
            brand = self.brand_entry.get()
            item_name = self.item_entry.get()
            price = float(self.price_entry.get())

            if brand and item_name and price >= 0:
                self.blockchain.add_block(self.next_uid, brand, item_name, price)
                self.next_uid += 1
                self.refresh_display()
                self.clear_entries()
                messagebox.showinfo("Success", "Item added to blockchain!")
            else:
                messagebox.showerror("Error", "Please fill all fields with valid values!")
        except ValueError:
            messagebox.showerror("Error", "Price must be a valid number!")

    def clear_entries(self):
        self.brand_entry.delete(0, tk.END)
        self.item_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

    def refresh_display(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        current = self.blockchain.head
        while current:
            self.tree.insert("", "end", values=(
                current.uid,
                current.brand,
                current.item_name,
                current.price,
                current.timestamp,
                current.hash
            ))
            current = current.next

    def validate_chain(self):
        if self.blockchain.validate_chain():
            messagebox.showinfo("Validation", "✅ Blockchain is valid and secure!")
        else:
            messagebox.showerror("Validation", "⚠️ Blockchain has been tampered with!")

def main():
    root = tk.Tk()
    app = BlockchainGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()