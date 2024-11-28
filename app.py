import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Manager Pro")
        self.root.geometry("1000x600")
        self.root.configure(bg="white")

        # Header
        header_frame = tk.Frame(self.root, bg="#2196F3", pady=10)
        header_frame.pack(fill=tk.X)

        logo_label = tk.Label(header_frame, text="CSV", bg="white", fg="#2196F3", font=('Helvetica', 18, 'bold'), width=4, height=2)
        logo_label.pack(side=tk.LEFT, padx=(20, 10))

        title_label = tk.Label(header_frame, text="CSV Data Manager Pro", bg="#2196F3", fg="white", font=('Helvetica', 18, 'bold'))
        title_label.pack(side=tk.LEFT)

        # Toolbar
        toolbar_frame = tk.Frame(self.root, bg="white")
        toolbar_frame.pack(fill=tk.X, pady=10)

        upload_button = tk.Button(toolbar_frame, text="Upload CSV", command=self.upload_csv, bg="#4CAF50", fg="white", font=('Helvetica', 12, 'bold'))
        upload_button.pack(side=tk.LEFT, padx=10)

        view_button = tk.Button(toolbar_frame, text="View Selected", command=self.show_selected, bg="#2196F3", fg="white", font=('Helvetica', 12, 'bold'))
        view_button.pack(side=tk.LEFT, padx=10)

        # Table
        self.tree = ttk.Treeview(self.root, columns=(), show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Status bar
        self.status_var = tk.StringVar(value="Ready to import CSV file")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w', padx=10, bg="white")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])

        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                data = list(csv_reader)

                if not data:
                    messagebox.showwarning("Warning", "The CSV file is empty!")
                    return

                columns = list(data[0].keys())
                self.tree.config(columns=columns)

                for col in columns:
                    self.tree.heading(col, text=col)
                    self.tree.column(col, anchor=tk.W)

                for item in self.tree.get_children():
                    self.tree.delete(item)

                for row in data:
                    self.tree.insert("", tk.END, values=list(row.values()))

                self.status_var.set(f"Loaded {len(data)} records from {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Error loading CSV: {str(e)}")
            self.status_var.set("Error loading CSV file")

    def show_selected(self):
        selected_items = self.tree.selection()

        if not selected_items:
            messagebox.showinfo("Info", "No items selected")
            return

        top = tk.Toplevel(self.root)
        top.title("Selected Records")
        top.geometry("600x400")

        text = tk.Text(top, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for item_id in selected_items:
            values = self.tree.item(item_id)['values']
            text.insert(tk.END, f"{values}\n\n")

        self.status_var.set(f"Showing {len(selected_items)} selected items")

def main():
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
