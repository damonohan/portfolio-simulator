#!/usr/bin/env python3
"""
Simulation Results Viewer

A standalone GUI tool for viewing and filtering portfolio simulation results
from the SQLite database in a tabular format.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd
import os
import platform
import sys
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for compatibility

class SimulationResultsViewer:
    """A table-based viewer for portfolio simulation results"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Portfolio Simulation Results Viewer")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Set up styling
        self.setup_styles()
        
        # Create variables
        self.db_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Please select a simulation database to view results")
        self.current_df = None  # Store the current dataframe
        self.filter_vars = {}   # Store filter variables
        
        # Create main layout
        self.create_layout()
        
        # Check for default database
        default_db = "./simulation_results/historical_retirement_2024_03/simulation_db.sqlite"
        if os.path.exists(default_db):
            self.db_path.set(default_db)
            self.load_database()
    
    def setup_styles(self):
        """Configure ttk styles for the application"""
        self.style = ttk.Style()
        
        # Configure colors based on platform
        if platform.system() == "Darwin":  # macOS
            bg_color = "#F5F5F7"
            header_bg = "#007AFF"
        else:  # Windows/Linux
            bg_color = "#F0F0F0"
            header_bg = "#0078D7"
            
        text_color = "#333333"
        accent_color = "#0078D7"
            
        # Configure base styles
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=text_color)
        self.style.configure("TButton", foreground=text_color)
        
        # Configure header style
        self.style.configure("Header.TLabel", 
                            font=("Helvetica", 14, "bold"), 
                            foreground="#FFFFFF", 
                            background=header_bg,
                            padding=10)
                            
        # Configure Treeview (table) styles
        self.style.configure("Treeview", 
                            font=("Helvetica", 11),
                            rowheight=25)
        self.style.configure("Treeview.Heading", 
                            font=("Helvetica", 12, "bold"),
                            background=accent_color,
                            foreground="white")
    
    def create_layout(self):
        """Create the main application layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section - Header and database selection
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Header
        header_frame = ttk.Frame(top_frame)
        header_frame.pack(fill=tk.X)
        header_label = ttk.Label(header_frame, 
                                text="Portfolio Simulation Results Viewer", 
                                style="Header.TLabel")
        header_label.pack(fill=tk.X)
        
        # Database selection
        db_frame = ttk.Frame(top_frame)
        db_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(db_frame, text="Database:").pack(side=tk.LEFT, padx=(0, 5))
        db_entry = ttk.Entry(db_frame, textvariable=self.db_path, width=60)
        db_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(db_frame, text="Browse...", command=self.browse_database)
        browse_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        load_btn = ttk.Button(db_frame, text="Load Database", command=self.load_database)
        load_btn.pack(side=tk.LEFT)
        
        # Filter section
        filter_frame = ttk.LabelFrame(main_frame, text="Filters")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # We'll populate this dynamically when a database is loaded
        self.filter_frame_inner = ttk.Frame(filter_frame)
        self.filter_frame_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Table section
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create table with scrollbars
        self.create_results_table(table_frame)
        
        # Bottom section - Status and export
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Status bar
        status_label = ttk.Label(bottom_frame, textvariable=self.status_text, font=("Helvetica", 10, "italic"))
        status_label.pack(side=tk.LEFT)
        
        # Export button
        export_btn = ttk.Button(bottom_frame, text="Export to CSV", command=self.export_to_csv)
        export_btn.pack(side=tk.RIGHT)
    
    def create_results_table(self, parent):
        """Create the results table with scrollbars"""
        # Container for the table and scrollbars
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        x_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        y_scrollbar = ttk.Scrollbar(table_container)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the table (empty initially - we'll populate when data is loaded)
        self.results_table = ttk.Treeview(table_container, 
                                          show="headings",
                                          yscrollcommand=y_scrollbar.set,
                                          xscrollcommand=x_scrollbar.set)
        
        # Configure scrollbars
        x_scrollbar.config(command=self.results_table.xview)
        y_scrollbar.config(command=self.results_table.yview)
        
        # Pack the table
        self.results_table.pack(fill=tk.BOTH, expand=True)
        
        # Bind sorting event
        self.results_table.bind("<Button-1>", self.handle_click)
    
    def browse_database(self):
        """Open a file dialog to select a database file"""
        filename = filedialog.askopenfilename(
            title="Select Simulation Database",
            filetypes=[("SQLite files", "*.sqlite"), ("All files", "*.*")]
        )
        if filename:
            self.db_path.set(filename)
    
    def load_database(self):
        """Load simulation results from the selected database"""
        db_path = self.db_path.get()
        if not db_path or not os.path.exists(db_path):
            messagebox.showerror("Error", "Please select a valid database file")
            return
        
        try:
            # Connect to database
            self.conn = sqlite3.connect(db_path)
            
            # Load main simulation table
            query = """
                SELECT 
                    sim_id, start_year, portfolio_type, 
                    equity_allocation, note_allocation, bond_allocation,
                    protection_level, withdrawal_rate, time_horizon, 
                    terminal_value, success_flag, cagr, max_drawdown, volatility
                FROM simulations
                ORDER BY start_year, portfolio_type, protection_level
            """
            df = pd.read_sql_query(query, self.conn)
            
            # Format numeric columns
            df['equity_allocation'] = df['equity_allocation'] * 100
            df['note_allocation'] = df['note_allocation'] * 100
            df['bond_allocation'] = df['bond_allocation'] * 100
            df['protection_level'] = df['protection_level'] * 100
            df['withdrawal_rate'] = df['withdrawal_rate'] * 100
            df['cagr'] = df['cagr'] * 100
            df['max_drawdown'] = df['max_drawdown'] * 100
            df['volatility'] = df['volatility'] * 100
            
            # Save dataframe
            self.current_df = df
            
            # Update status
            self.status_text.set(f"Loaded {len(df)} simulation results")
            
            # Update the table
            self.populate_table(df)
            
            # Set up filters based on loaded data
            self.setup_filters(df)
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading database: {str(e)}")
    
    def populate_table(self, df):
        """Populate the results table with the given dataframe"""
        # Clear existing data
        for item in self.results_table.get_children():
            self.results_table.delete(item)
        
        # Configure columns
        columns = list(df.columns)
        self.results_table["columns"] = columns
        
        # Configure column headings and widths
        for col in columns:
            # Choose a reasonable width based on column name and data type
            if col == 'sim_id':
                width = 250
            elif col == 'terminal_value':
                width = 150
            elif col in ['equity_allocation', 'note_allocation', 'bond_allocation', 
                       'protection_level', 'withdrawal_rate', 'cagr', 'max_drawdown', 'volatility']:
                width = 100
            else:
                width = 120
            
            # Configure the column
            self.results_table.column(col, width=width, minwidth=80)
            self.results_table.heading(col, text=col.replace('_', ' ').title(), command=lambda c=col: self.sort_column(c))
        
        # Format the data for display
        for i, row in df.iterrows():
            formatted_row = []
            for col in columns:
                value = row[col]
                # Format numbers for better readability
                if col == 'terminal_value':
                    formatted_value = f"${value:,.2f}"
                elif col in ['equity_allocation', 'note_allocation', 'bond_allocation', 
                           'protection_level', 'withdrawal_rate', 'cagr', 'max_drawdown', 'volatility']:
                    formatted_value = f"{value:.2f}%"
                elif col == 'success_flag':
                    formatted_value = "Yes" if value == 1 else "No"
                else:
                    formatted_value = str(value)
                formatted_row.append(formatted_value)
            
            self.results_table.insert('', tk.END, values=formatted_row)
    
    def setup_filters(self, df):
        """Set up filter controls based on the loaded data"""
        # Clear existing filters
        for widget in self.filter_frame_inner.winfo_children():
            widget.destroy()
        self.filter_vars = {}
        
        # Create filter UI
        filters_to_add = [
            ('start_year', 'Start Year'), 
            ('portfolio_type', 'Portfolio Type'),
            ('protection_level', 'Protection Level'),
            ('withdrawal_rate', 'Withdrawal Rate'),
            ('time_horizon', 'Time Horizon')
        ]
        
        # Organize in a grid layout
        row, col = 0, 0
        max_col = 5  # Number of columns in the grid
        
        for column, label in filters_to_add:
            # Frame for this filter
            filter_group = ttk.Frame(self.filter_frame_inner)
            filter_group.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            # Label
            ttk.Label(filter_group, text=label + ":").pack(anchor='w')
            
            # Get unique values for this column
            unique_values = sorted(df[column].unique())
            
            # Create variable and widget based on number of unique values
            if len(unique_values) <= 10:  # Use checkbuttons for small number of options
                # Create a sub-frame for the checkbuttons
                check_frame = ttk.Frame(filter_group)
                check_frame.pack(fill='x', padx=(10, 0))
                
                # Create a dict to hold variables for this filter
                self.filter_vars[column] = {}
                
                # Create checkbuttons for each value
                for value in unique_values:
                    var = tk.BooleanVar(value=True)
                    self.filter_vars[column][value] = var
                    display_val = f"{value:.1f}%" if column in ['protection_level', 'withdrawal_rate'] else value
                    cb = ttk.Checkbutton(check_frame, text=str(display_val), variable=var, 
                                        command=self.apply_filters)
                    cb.pack(anchor='w')
            else:  # Use a dropdown for many options
                self.filter_vars[column] = tk.StringVar(value='All')
                values = ['All'] + [str(v) for v in unique_values]
                dropdown = ttk.Combobox(filter_group, textvariable=self.filter_vars[column], 
                                      values=values, state='readonly', width=15)
                dropdown.pack(fill='x', padx=(10, 0), pady=(5, 0))
                dropdown.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
            
            # Update grid position
            col += 1
            if col >= max_col:
                col = 0
                row += 1
        
        # Add a "Reset Filters" button
        reset_btn = ttk.Button(self.filter_frame_inner, text="Reset Filters", command=self.reset_filters)
        reset_btn.grid(row=row+1, column=0, columnspan=max_col, pady=10)
    
    def apply_filters(self):
        """Apply selected filters to the data"""
        if self.current_df is None:
            return
        
        # Start with full dataset
        filtered_df = self.current_df.copy()
        
        # Apply each filter
        for column, filter_var in self.filter_vars.items():
            if isinstance(filter_var, dict):  # Checkbutton group
                # Get selected values
                selected_values = [value for value, var in filter_var.items() if var.get()]
                if selected_values:  # Only filter if at least one is selected
                    filtered_df = filtered_df[filtered_df[column].isin(selected_values)]
            else:  # Combobox
                selected_value = filter_var.get()
                if selected_value != 'All':
                    # Convert to appropriate type based on column
                    if column in ['start_year', 'time_horizon']:
                        selected_value = int(selected_value)
                    elif column in ['protection_level', 'withdrawal_rate']:
                        selected_value = float(selected_value)
                    filtered_df = filtered_df[filtered_df[column] == selected_value]
        
        # Update table
        self.populate_table(filtered_df)
        
        # Update status
        self.status_text.set(f"Showing {len(filtered_df)} of {len(self.current_df)} simulation results")
    
    def reset_filters(self):
        """Reset all filters to their default states"""
        for column, filter_var in self.filter_vars.items():
            if isinstance(filter_var, dict):  # Checkbutton group
                for var in filter_var.values():
                    var.set(True)
            else:  # Combobox
                filter_var.set('All')
        
        # Apply updated filters
        self.apply_filters()
    
    def handle_click(self, event):
        """Handle clicking on the table header for sorting"""
        region = self.results_table.identify_region(event.x, event.y)
        if region == "heading":
            column = self.results_table.identify_column(event.x)
            column_index = int(column.replace('#', '')) - 1
            column_name = self.results_table["columns"][column_index]
            self.sort_column(column_name)
    
    def sort_column(self, column):
        """Sort the table by the given column"""
        if self.current_df is None:
            return
        
        # Get current sorting key and order
        if hasattr(self, 'sort_column_name') and self.sort_column_name == column:
            # Toggle sort order if clicking the same column
            self.sort_ascending = not self.sort_ascending
        else:
            # Default to ascending for new sort column
            self.sort_column_name = column
            self.sort_ascending = True
        
        # Sort the dataframe
        df_sorted = self.current_df.sort_values(
            by=column, 
            ascending=self.sort_ascending,
            key=lambda x: x if x.name != 'sim_id' else x.str.extract(r'(\d+)_').astype(float)
        )
        
        # Apply any active filters
        self.current_df = df_sorted
        self.apply_filters()
    
    def export_to_csv(self):
        """Export the current filtered table view to a CSV file"""
        if self.current_df is None:
            messagebox.showwarning("No Data", "No data to export")
            return
        
        # Get currently visible rows (after filtering)
        visible_items = self.results_table.get_children()
        if not visible_items:
            messagebox.showwarning("No Data", "No data to export")
            return
        
        # Get values for visible rows
        visible_data = []
        for item in visible_items:
            values = self.results_table.item(item, 'values')
            visible_data.append(values)
        
        # Create dataframe from visible data
        columns = self.results_table["columns"]
        visible_df = pd.DataFrame(visible_data, columns=columns)
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                visible_df.to_csv(filename, index=False)
                messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")

def main():
    root = tk.Tk()
    if platform.system() == 'Darwin':  # macOS
        # Fix for Mac GUI rendering issues
        os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
    app = SimulationResultsViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 