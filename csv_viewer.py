import tkinter as tk
from tkinter import ttk, filedialog
import csv
from typing import List, Dict

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer")
        self.root.geometry("800x600")
        
        # Initialize variables
        self.data: List[Dict] = []
        self.checkboxes = []
        self.var_dict = {}
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create upload button
        self.upload_button = ttk.Button(
            self.main_frame,
            text="Upload CSV",
            command=self.upload_csv
        )
        self.upload_button.grid(row=0, column=0, pady=10, sticky=tk.W)
        
        # Create frame for list
        self.list_frame = ttk.Frame(self.main_frame)
        self.list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.list_frame)
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Create select all button
        self.select_all_var = tk.BooleanVar()
        self.select_all_checkbox = ttk.Checkbutton(
            self.main_frame,
            text="Select All",
            variable=self.select_all_var,
            command=self.toggle_all
        )
        self.select_all_checkbox.grid(row=2, column=0, pady=5, sticky=tk.W)
        
        # Create get selected button
        self.get_selected_button = ttk.Button(
            self.main_frame,
            text="Get Selected Items",
            command=self.show_selected
        )
        self.get_selected_button.grid(row=3, column=0, pady=5, sticky=tk.W)

    def upload_csv(self):
        # Open file dialog
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            # Clear previous data
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.data = []
            self.checkboxes = []
            self.var_dict = {}
            
            # Read CSV file
            with open(file_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                self.data = list(csv_reader)
            
            # Create checkboxes for each row
            for i, row in enumerate(self.data):
                var = tk.BooleanVar()
                self.var_dict[i] = var
                
                # Create a frame for each row
                row_frame = ttk.Frame(self.scrollable_frame)
                row_frame.pack(fill="x", padx=5, pady=2)
                
                # Create checkbox
                cb = ttk.Checkbutton(
                    row_frame,
                    variable=var,
                    text=f"Row {i+1}: {', '.join(f'{k}: {v}' for k, v in row.items())}"
                )
                cb.pack(side="left")
                self.checkboxes.append(cb)

    def toggle_all(self):
        # Get the state from the select all checkbox
        state = self.select_all_var.get()
        
        # Set all checkboxes to that state
        for var in self.var_dict.values():
            var.set(state)

    def show_selected(self):
        # Get selected items
        selected = []
        for i, var in self.var_dict.items():
            if var.get():
                selected.append(self.data[i])
        
        # Create a new window to show selected items
        top = tk.Toplevel(self.root)
        top.title("Selected Items")
        top.geometry("600x400")
        
        # Create text widget
        text = tk.Text(top, wrap=tk.WORD)
        text.pack(fill="both", expand=True)
        
        # Insert selected items
        if selected:
            for item in selected:
                text.insert(tk.END, f"{item}\n\n")
        else:
            text.insert(tk.END, "No items selected")

def main():
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
