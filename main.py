import csv
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk


class CustomerLookupApp:
    def __init__(self, root, csv_path):
        self.root = root
        self.csv_path = csv_path
        self.records = []
        self.filtered_records = []
        self.headers = []
        self.year_options = ["All"]

        self.root.title("Customer Lookup App")
        self.root.geometry("1000x650")
        self.root.minsize(900, 600)
        self.root.configure(bg="#f4f7fb")

        self._setup_styles()
        self._build_ui()
        self._load_data()

    def _setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1f3b63")
        style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"), foreground="#1f3b63")
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=6)
        style.configure("TButton", padding=(10, 6))
        style.map("TButton", background=[("active", "#3b82f6")], foreground=[("active", "white")])

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        title = ttk.Label(main_frame, text="Customer Records Lookup", style="Title.TLabel")
        title.pack(anchor="w", pady=(0, 12))

        subtitle = ttk.Label(
            main_frame,
            text="Search and filter records quickly with a clean, professional interface.",
            foreground="#5b6b7a",
        )
        subtitle.pack(anchor="w", pady=(0, 18))

        controls = ttk.LabelFrame(main_frame, text="Search & Filter", padding=12)
        controls.pack(fill="x", pady=(0, 14))

        controls_grid = ttk.Frame(controls)
        controls_grid.pack(fill="x")

        ttk.Label(controls_grid, text="Search:", style="Header.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(controls_grid, textvariable=self.search_var, width=40)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        self.search_entry.bind("<Return>", lambda event: self._apply_filters())

        ttk.Label(controls_grid, text="Year:", style="Header.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.year_var = tk.StringVar(value="All")
        self.year_combo = ttk.Combobox(controls_grid, textvariable=self.year_var, state="readonly", width=15)
        self.year_combo.grid(row=0, column=3, sticky="ew", padx=(0, 12))

        self.search_btn = ttk.Button(controls_grid, text="Apply Filters", command=self._apply_filters)
        self.search_btn.grid(row=0, column=4, padx=(0, 8))

        self.reset_btn = ttk.Button(controls_grid, text="Reset", command=self._reset_filters)
        self.reset_btn.grid(row=0, column=5)

        controls_grid.columnconfigure(1, weight=1)

        self.status_var = tk.StringVar(value="Loading records...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, foreground="#4b5563")
        status_bar.pack(anchor="w", pady=(0, 10))

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.heading("#0", text="")

    def _load_data(self):
        if not os.path.exists(self.csv_path):
            messagebox.showerror("File not found", f"Could not find: {self.csv_path}")
            self.root.destroy()
            return

        try:
            with open(self.csv_path, "r", newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                self.headers = reader.fieldnames or []
                self.records = []
                for row in reader:
                    self.records.append(row)

            if not self.headers:
                messagebox.showwarning("No data", "The selected CSV file appears to be empty.")
                self.root.destroy()
                return

            self._configure_columns()
            self._populate_year_filter()
            self._apply_filters()

        except Exception as exc:
            messagebox.showerror("Load error", f"Unable to read the CSV file:\n{exc}")
            self.root.destroy()

    def _configure_columns(self):
        self.tree.delete(*self.tree.get_children())
        self.tree.configure(columns=self.headers)
        for column in self.headers:
            self.tree.heading(column, text=column.replace("_", " ").title())
            self.tree.column(column, anchor="w", width=140, minwidth=100)

    def _populate_year_filter(self):
        years = set()
        for row in self.records:
            value = row.get("date", "")
            if not value:
                continue
            try:
                parsed = datetime.strptime(value, "%Y-%m")
                years.add(str(parsed.year))
            except ValueError:
                continue

        self.year_options = ["All"] + sorted(years)
        self.year_combo["values"] = self.year_options
        self.year_var.set("All")

    def _reset_filters(self):
        self.search_var.set("")
        self.year_var.set("All")
        self._apply_filters()

    def _apply_filters(self):
        query = self.search_var.get().strip().lower()
        selected_year = self.year_var.get()

        filtered = []
        for row in self.records:
            if query:
                matches_query = any(query in str(value).lower() for value in row.values())
                if not matches_query:
                    continue

            if selected_year != "All":
                date_value = row.get("date", "")
                try:
                    parsed = datetime.strptime(date_value, "%Y-%m")
                except ValueError:
                    continue
                if str(parsed.year) != selected_year:
                    continue

            filtered.append(row)

        self.filtered_records = filtered
        self._render_table()

    def _render_table(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.filtered_records:
            values = [row.get(header, "") for header in self.headers]
            self.tree.insert("", "end", values=values)

        self.status_var.set(f"Showing {len(self.filtered_records)} of {len(self.records)} records")


if __name__ == "__main__":
    data_file = os.path.join(os.path.dirname(__file__), "monthly_sales.csv")
    root = tk.Tk()
    app = CustomerLookupApp(root, data_file)
    root.mainloop()
