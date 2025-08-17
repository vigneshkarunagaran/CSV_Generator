import os
import csv
import random
import string
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# -----------------------------
# Data Generation Functions
# -----------------------------
def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_date(start_year=2000, end_year=2025):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")

def generate_column_data(col_def, num_rows):
    values = set()
    data = []

    if isinstance(col_def['type'], list):
        options = col_def['type']
        if not col_def.get("allow_duplicates", True) and len(options) < num_rows:
            raise ValueError(f"Cannot generate {num_rows} unique values from {options}")
        while len(data) < num_rows:
            value = random.choice(options)
            if col_def.get("allow_duplicates", True) or value not in values:
                data.append(value)
                values.add(value)
        return data

    datatype = col_def['type']
    allow_duplicates = col_def.get("allow_duplicates", True)

    while len(data) < num_rows:
        if datatype == "int":
            value = random.randint(1, 10000)
        elif datatype == "float":
            value = round(random.uniform(1.0, 10000.0), 2)
        elif datatype == "str":
            value = generate_random_string()
        elif datatype == "date":
            value = generate_random_date()
        else:
            raise ValueError(f"Unsupported datatype: {datatype}")

        if allow_duplicates or value not in values:
            data.append(value)
            values.add(value)

    return data

def generate_csv(schema, num_rows, output_file):
    column_data = {}
    for col in schema:
        column_data[col["name"]] = generate_column_data(col, num_rows)

    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([col["name"] for col in schema])
        for i in range(num_rows):
            writer.writerow([column_data[col["name"]][i] for col in schema])

# -----------------------------
# Tkinter UI
# -----------------------------
class CSVGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Generator")

        self.schema = []
        self.output_folder = tk.StringVar()
        self.num_rows = tk.IntVar(value=100)
        self.num_files = tk.IntVar(value=1)

        # Frame for schema
        schema_frame = ttk.LabelFrame(root, text="Schema Definition")
        schema_frame.pack(fill="x", padx=10, pady=5)

        self.schema_tree = ttk.Treeview(schema_frame, columns=("Name", "Type", "Duplicates"), show="headings")
        self.schema_tree.heading("Name", text="Column Name")
        self.schema_tree.heading("Type", text="Type / Values")
        self.schema_tree.heading("Duplicates", text="Allow Duplicates")
        self.schema_tree.pack(fill="x", pady=5)

        add_btn = ttk.Button(schema_frame, text="Add Column", command=self.add_column_dialog)
        add_btn.pack(pady=5)

        # Config frame
        config_frame = ttk.LabelFrame(root, text="Config")
        config_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(config_frame, text="Rows per file:").grid(row=0, column=0, sticky="w")
        ttk.Entry(config_frame, textvariable=self.num_rows).grid(row=0, column=1)

        ttk.Label(config_frame, text="Number of files:").grid(row=1, column=0, sticky="w")
        ttk.Entry(config_frame, textvariable=self.num_files).grid(row=1, column=1)

        ttk.Label(config_frame, text="Output folder:").grid(row=2, column=0, sticky="w")
        ttk.Entry(config_frame, textvariable=self.output_folder, width=30).grid(row=2, column=1)
        ttk.Button(config_frame, text="Browse", command=self.browse_folder).grid(row=2, column=2)

        # Generate button
        gen_btn = ttk.Button(root, text="Generate CSVs", command=self.generate_files)
        gen_btn.pack(pady=10)

    def add_column_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Column")

        tk.Label(dialog, text="Column Name:").grid(row=0, column=0)
        name_entry = tk.Entry(dialog)
        name_entry.grid(row=0, column=1)

        tk.Label(dialog, text="Type (int, float, str, date OR comma separated values):").grid(row=1, column=0)
        type_entry = tk.Entry(dialog)
        type_entry.grid(row=1, column=1)

        dup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(dialog, text="Allow Duplicates", variable=dup_var).grid(row=2, columnspan=2)

        def save_column():
            col_name = name_entry.get().strip()
            col_type = type_entry.get().strip()
            if not col_name or not col_type:
                messagebox.showerror("Error", "Column name and type required")
                return
            if "," in col_type:
                col_type = [v.strip() for v in col_type.split(",")]
            self.schema.append({"name": col_name, "type": col_type, "allow_duplicates": dup_var.get()})
            self.schema_tree.insert("", "end", values=(col_name, col_type, dup_var.get()))
            dialog.destroy()

        ttk.Button(dialog, text="Add", command=save_column).grid(row=3, columnspan=2)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def generate_files(self):
        if not self.schema:
            messagebox.showerror("Error", "No schema defined!")
            return
        if not self.output_folder.get():
            messagebox.showerror("Error", "Select output folder!")
            return
        os.makedirs(self.output_folder.get(), exist_ok=True)

        for i in range(1, self.num_files.get() + 1):
            output_file = os.path.join(self.output_folder.get(), f"data{i}.csv")
            generate_csv(self.schema, self.num_rows.get(), output_file)

        messagebox.showinfo("Success", f"Generated {self.num_files.get()} CSV file(s).")


