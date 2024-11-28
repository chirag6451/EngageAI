import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer")
        self.root.geometry("800x600")
        
        # Create the main frame with padding
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the header
        header_label = tk.Label(
            self.main_frame,
            text="CSV Data Viewer",
            font=('Helvetica', 18, 'bold'),
            pady=10
        )
        header_label.pack()
        
        # Create button frame
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add buttons
        self.upload_btn = tk.Button(
            button_frame,
            text="Upload CSV",
            command=self.upload_csv,
            width=15,
            bg='#4CAF50',
            fg='white',
            font=('Helvetica', 10)
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        # Select all checkbox
        self.select_all_var = tk.BooleanVar()
        self.select_all_cb = tk.Checkbutton(
            button_frame,
            text="Select All",
            variable=self.select_all_var,
            command=self.toggle_all
        )
        self.select_all_cb.pack(side=tk.LEFT, padx=20)
        
        # View selected button
        self.view_btn = tk.Button(
            button_frame,
            text="View Selected",
            command=self.show_selected,
            width=15,
            bg='#2196F3',
            fg='white',
            font=('Helvetica', 10)
        )
        self.view_btn.pack(side=tk.LEFT, padx=5)
        
        # Create frame for the list
        list_frame = tk.Frame(self.main_frame, relief=tk.SUNKEN, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create canvas
        self.canvas = tk.Canvas(list_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=scrollbar.set)
        
        # Create frame for checkboxes
        self.checkbox_frame = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0, 0), window=self.checkbox_frame, anchor='nw')
        
        # Add status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to import CSV file")
        self.status_bar = tk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor='w',
            padx=10,
            pady=5
        )
        self.status_bar.pack(fill=tk.X)
        
        # Initialize variables
        self.data = []
        self.checkboxes = []
        self.var_dict = {}
        
        # Configure canvas scrolling
        self.checkbox_frame.bind('<Configure>', self._configure_canvas)
        self.canvas.bind('<Configure>', self._configure_canvas_window)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _configure_canvas(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _configure_canvas_window(self, event):
        self.canvas.itemconfig(1, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def upload_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
            
        # Clear previous data
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        self.data = []
        self.checkboxes = []
        self.var_dict = {}
        
        try:
            with open(file_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                self.data = list(csv_reader)
            
            # Create checkboxes for each row
            for i, row in enumerate(self.data):
                var = tk.BooleanVar()
                self.var_dict[i] = var
                
                frame = tk.Frame(self.checkbox_frame, bg='white')
                frame.pack(fill=tk.X, padx=5, pady=2)
                
                cb = tk.Checkbutton(
                    frame,
                    variable=var,
                    text=f"Row {i+1}: " + " | ".join(f"{k}: {v}" for k, v in row.items()),
                    bg='white',
                    anchor='w',
                    justify=tk.LEFT
                )
                cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.checkboxes.append(cb)
            
            self.status_var.set(f"Loaded {len(self.data)} records from {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading CSV: {str(e)}")
            self.status_var.set("Error loading CSV file")

    def toggle_all(self):
        state = self.select_all_var.get()
        for var in self.var_dict.values():
            var.set(state)
        self.status_var.set(f"{'Selected' if state else 'Deselected'} all items")

    def show_selected(self):
        selected = []
        for i, var in self.var_dict.items():
            if var.get():
                selected.append(self.data[i])
        
        if not selected:
            messagebox.showinfo("Info", "No items selected")
            return
        
        # Create new window for selected items
        top = tk.Toplevel(self.root)
        top.title("Selected Items")
        top.geometry("600x400")
        
        # Add header
        tk.Label(
            top,
            text="Selected Records",
            font=('Helvetica', 14, 'bold'),
            pady=10
        ).pack()
        
        # Create text widget with scrollbar
        frame = tk.Frame(top)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text.yview)
        
        for item in selected:
            formatted_item = "\n".join(f"{k}: {v}" for k, v in item.items())
            text.insert(tk.END, f"{formatted_item}\n\n{'='*40}\n\n")
        
        self.status_var.set(f"Showing {len(selected)} selected items")

def main():
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
