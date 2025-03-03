#!/usr/bin/env python3
"""
Portfolio Simulator GUI

This module provides a graphical user interface for the Portfolio Simulator,
allowing users to configure and run simulations with structured notes.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import pandas as pd
from datetime import datetime
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class PortfolioSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HALO Portfolio Simulator")
        self.root.geometry("1200x900")  # Increased height from 800 to 900
        self.root.resizable(True, True)
        
        # Position window in the center of the screen
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Calculate position coordinates
        x = (screen_width - 1200) // 2
        y = (screen_height - 900) // 2
        
        # Set window position
        self.root.geometry(f"1200x900+{x}+{y}")
        
        # Define colors
        self.colors = {
            "primary": "#101e57",  # Dark blue like in HALO logo
            "secondary": "#3498db",  # Lighter blue for accents
            "bg_light": "#f5f5f5",  # Light background
            "bg_white": "#ffffff",  # White background
            "text_dark": "#2c3e50",  # Dark text
            "border": "#d7dbdd",  # Light border color
            "growth_blue": "#0066cc"  # Blue color for the Growth button like in HALO
        }
        
        # Configure styles
        self.configure_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill='both', expand=True)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.results_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text="Simulation Setup")
        self.notebook.add(self.results_tab, text="Results")
        
        # Setup the input form
        self.create_setup_form()
        
        # Setup the results view (initially empty)
        self.create_results_view()
        
        # Set default values
        self.set_default_values()
    
    def configure_styles(self):
        # Configure ttk styles
        style = ttk.Style()
        
        # Main styles
        style.configure("TFrame", background=self.colors["bg_light"])
        style.configure("TLabel", background=self.colors["bg_light"], foreground=self.colors["text_dark"], font=('Helvetica', 11))
        style.configure("TButton", background=self.colors["primary"], foreground="white", font=('Helvetica', 11))
        style.configure("TEntry", background=self.colors["bg_white"], font=('Helvetica', 11))
        style.configure("TSpinbox", background=self.colors["bg_white"], font=('Helvetica', 11))
        style.configure("TCombobox", background=self.colors["bg_white"], font=('Helvetica', 11))
        style.configure("TCheckbutton", background=self.colors["bg_light"], foreground=self.colors["text_dark"], font=('Helvetica', 11))
        
        # Notebook tab styles
        style.configure("TNotebook", background=self.colors["bg_light"], tabposition='n')
        style.configure("TNotebook.Tab", background=self.colors["bg_light"], font=('Helvetica', 12))
        style.map("TNotebook.Tab",
                 background=[("selected", self.colors["primary"])],
                 foreground=[("selected", "white")])

        # Custom styles
        style.configure("Sidebar.TFrame", background=self.colors["bg_white"], relief="ridge", borderwidth=1)
        style.configure("Content.TFrame", background=self.colors["bg_white"], relief="ridge", borderwidth=1)
        
        # Make section headers bigger and bolder
        style.configure("Header.TLabel", 
                       background=self.colors["bg_white"], 
                       foreground=self.colors["primary"], 
                       font=('Helvetica', 18, 'bold'))  # Increased from 16 to 18
        
        # Style for section headers
        style.configure("SectionHeader.TLabel", 
                       background=self.colors["bg_white"], 
                       foreground=self.colors["primary"], 
                       font=('Helvetica', 16, 'bold'))  # Increased from 14 to 16
        
        # Style for sidebar headers
        style.configure("SidebarHeader.TLabel", 
                       background=self.colors["bg_white"], 
                       foreground=self.colors["primary"], 
                       font=('Helvetica', 14, 'bold'),  # Increased from 12 to 14
                       padding=(5, 10, 5, 10))
    
    def create_setup_form(self):
        # Create a container frame with two main areas (sidebar and content)
        container = ttk.Frame(self.setup_tab)
        container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create HALO logo in the upper left corner
        logo_frame = ttk.Frame(container)
        logo_frame.pack(fill='x', pady=(0, 15), padx=5, anchor='w')
        
        # Create a text-based HALO logo with styling
        logo_label = tk.Label(logo_frame, 
                            text="HALO", 
                            font=('Arial', 30, 'bold'), 
                            fg=self.colors["primary"],
                            bg=self.colors["bg_light"],
                            padx=10)
        logo_label.pack(side=tk.LEFT, pady=5)
        
        # Create sidebar frame (left side - parameters)
        sidebar = ttk.Frame(container, style='Sidebar.TFrame', width=400)  # Increased from 350 to 400
        sidebar.pack(side=tk.LEFT, fill='y', padx=5, pady=5)
        sidebar.pack_propagate(False)  # Don't shrink
        
        # Create content frame (right side - data files and options)
        content = ttk.Frame(container, style='Content.TFrame')
        content.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        
        # Run button at the top of sidebar for better visibility
        run_frame = ttk.Frame(sidebar, style='Sidebar.TFrame')
        run_frame.pack(fill='x', pady=10, padx=10)
        
        # Add rocket ship emoji and make button bigger and more eye-catching
        run_button = tk.Button(run_frame, 
                              text="🚀 Run Simulation 🚀", 
                              command=self.run_simulation,
                              font=('Helvetica', 18, 'bold'),  # Even larger font
                              background="#FF5722",  # Bright orange color for more pop
                              foreground='black',  # Changed from white to black
                              activebackground="#E64A19",  # Darker orange when clicked
                              activeforeground='black',  # Changed from white to black
                              relief=tk.RAISED,
                              bd=2,
                              padx=15,  
                              pady=12,  # Increased padding
                              height=2)
        run_button.pack(fill='x')
        
        # SIMULATION PARAMETERS SECTION
        sim_params_frame = ttk.LabelFrame(sidebar, text="Simulation Parameters", padding=10)
        sim_params_frame.pack(fill='x', pady=5, padx=10)
        
        # Simulation period
        ttk.Label(sim_params_frame, text="Simulation Period", style="SectionHeader.TLabel").pack(fill='x', pady=(5, 10))
        
        # Start Year
        year_frame = ttk.Frame(sim_params_frame)
        year_frame.pack(fill='x', pady=5)
        ttk.Label(year_frame, text="Start Year:").pack(side=tk.LEFT)
        self.start_year_var = tk.StringVar()
        ttk.Entry(year_frame, textvariable=self.start_year_var, width=10).pack(side=tk.RIGHT)
        
        # End Year
        year_frame = ttk.Frame(sim_params_frame)
        year_frame.pack(fill='x', pady=5)
        ttk.Label(year_frame, text="End Year:").pack(side=tk.LEFT)
        self.end_year_var = tk.StringVar()
        ttk.Entry(year_frame, textvariable=self.end_year_var, width=10).pack(side=tk.RIGHT)
        
        # Initial Value
        init_frame = ttk.Frame(sim_params_frame)
        init_frame.pack(fill='x', pady=5)
        ttk.Label(init_frame, text="Initial Value ($):").pack(side=tk.LEFT)
        self.initial_value_var = tk.StringVar()
        ttk.Entry(init_frame, textvariable=self.initial_value_var, width=15).pack(side=tk.RIGHT)
        
        # STRUCTURED NOTE PARAMETERS SECTION
        note_params_frame = ttk.LabelFrame(sidebar, text="Structured Note Parameters", padding=10)
        note_params_frame.pack(fill='x', pady=10, padx=10)
        
        ttk.Label(note_params_frame, text="Protection", style="SectionHeader.TLabel").pack(fill='x', pady=(5, 10))
        
        # Protection Level
        prot_frame = ttk.Frame(note_params_frame)
        prot_frame.pack(fill='x', pady=5)
        ttk.Label(prot_frame, text="Protection Level (%):").pack(side=tk.LEFT)
        self.protection_level_var = tk.StringVar()
        ttk.Entry(prot_frame, textvariable=self.protection_level_var, width=10).pack(side=tk.RIGHT)
        
        # WITHDRAWAL PARAMETERS SECTION
        withdrawal_frame = ttk.LabelFrame(sidebar, text="Withdrawal Parameters", padding=10)
        withdrawal_frame.pack(fill='x', pady=10, padx=10)
        
        ttk.Label(withdrawal_frame, text="Withdrawal Strategy", style="SectionHeader.TLabel").pack(fill='x', pady=(5, 10))
        
        # Withdrawal Rate
        wd_rate_frame = ttk.Frame(withdrawal_frame)
        wd_rate_frame.pack(fill='x', pady=5)
        ttk.Label(wd_rate_frame, text="Withdrawal Rate (%):").pack(side=tk.LEFT)
        self.withdrawal_rate_var = tk.StringVar()
        ttk.Entry(wd_rate_frame, textvariable=self.withdrawal_rate_var, width=10).pack(side=tk.RIGHT)
        
        # Withdrawal Type
        wd_type_frame = ttk.Frame(withdrawal_frame)
        wd_type_frame.pack(fill='x', pady=5)
        ttk.Label(wd_type_frame, text="Withdrawal Type:").pack(side=tk.LEFT)
        self.withdrawal_type_var = tk.StringVar()
        withdrawal_types = ['fixed_percent', 'fixed_dollar', 'rmd']
        ttk.Combobox(wd_type_frame, textvariable=self.withdrawal_type_var, values=withdrawal_types, state="readonly").pack(side=tk.RIGHT)
        
        # Initial Age (for RMD)
        age_frame = ttk.Frame(withdrawal_frame)
        age_frame.pack(fill='x', pady=5)
        ttk.Label(age_frame, text="Initial Age:").pack(side=tk.LEFT)
        self.initial_age_var = tk.StringVar()
        ttk.Entry(age_frame, textvariable=self.initial_age_var, width=10).pack(side=tk.RIGHT)
        
        # ===== CONTENT AREA =====
        # Portfolio allocations in tabbed interface
        allocations_notebook = ttk.Notebook(content)
        allocations_notebook.pack(fill='both', expand=True, pady=5)
        
        # Traditional portfolio tab
        trad_tab = ttk.Frame(allocations_notebook)
        allocations_notebook.add(trad_tab, text="Traditional Portfolio")
        
        # Traditional Portfolio Allocations
        trad_frame = ttk.LabelFrame(trad_tab, text="Traditional Portfolio Allocations", padding=10)
        trad_frame.pack(fill='x', pady=10, padx=10)
        
        ttk.Label(trad_frame, text="S&P 500 Allocation (%):").grid(row=0, column=0, sticky='w', pady=5)
        self.trad_sp500_var = tk.StringVar()
        ttk.Entry(trad_frame, textvariable=self.trad_sp500_var, width=10).grid(row=0, column=1, sticky='w', padx=5)
        
        ttk.Label(trad_frame, text="Bonds Allocation (%):").grid(row=1, column=0, sticky='w', pady=5)
        self.trad_bonds_var = tk.StringVar()
        ttk.Entry(trad_frame, textvariable=self.trad_bonds_var, width=10).grid(row=1, column=1, sticky='w', padx=5)
        
        # Structured portfolio tab
        struct_tab = ttk.Frame(allocations_notebook)
        allocations_notebook.add(struct_tab, text="Structured Portfolio")
        
        # Structured Portfolio Allocations
        struct_frame = ttk.LabelFrame(struct_tab, text="Structured Portfolio Allocations", padding=10)
        struct_frame.pack(fill='x', pady=10, padx=10)
        
        ttk.Label(struct_frame, text="S&P 500 Allocation (%):").grid(row=0, column=0, sticky='w', pady=5)
        self.struct_sp500_var = tk.StringVar()
        ttk.Entry(struct_frame, textvariable=self.struct_sp500_var, width=10).grid(row=0, column=1, sticky='w', padx=5)
        
        ttk.Label(struct_frame, text="Bonds Allocation (%):").grid(row=1, column=0, sticky='w', pady=5)
        self.struct_bonds_var = tk.StringVar()
        ttk.Entry(struct_frame, textvariable=self.struct_bonds_var, width=10).grid(row=1, column=1, sticky='w', padx=5)
        
        ttk.Label(struct_frame, text="Notes Allocation (%):").grid(row=2, column=0, sticky='w', pady=5)
        self.struct_notes_var = tk.StringVar()
        ttk.Entry(struct_frame, textvariable=self.struct_notes_var, width=10).grid(row=2, column=1, sticky='w', padx=5)
        
        # DATA FILES SECTION (RIGHT SIDE)
        files_frame = ttk.LabelFrame(content, text="Data Sources", padding=10)
        files_frame.pack(fill='x', expand=True, pady=10, padx=10)
        
        ttk.Label(files_frame, text="Input Files", style="SectionHeader.TLabel").pack(fill='x', pady=(5, 10))
        
        # S&P 500 File
        sp_file_frame = ttk.Frame(files_frame)
        sp_file_frame.pack(fill='x', pady=5)
        ttk.Label(sp_file_frame, text="S&P 500 Returns:").pack(side=tk.LEFT)
        self.sp500_file_var = tk.StringVar()
        ttk.Entry(sp_file_frame, textvariable=self.sp500_file_var).pack(side=tk.LEFT, fill='x', expand=True, padx=(5, 5))
        # Use regular tk Button for consistent styling
        tk.Button(sp_file_frame, 
                 text="Browse", 
                 command=lambda: self.browse_file(self.sp500_file_var),
                 font=('Helvetica', 11),
                 background=self.colors["primary"],
                 foreground='black',
                 activebackground=self.colors["secondary"],
                 activeforeground='black').pack(side=tk.RIGHT)
        
        # Bond File
        bond_file_frame = ttk.Frame(files_frame)
        bond_file_frame.pack(fill='x', pady=5)
        ttk.Label(bond_file_frame, text="Bond Returns:").pack(side=tk.LEFT)
        self.bond_file_var = tk.StringVar()
        ttk.Entry(bond_file_frame, textvariable=self.bond_file_var).pack(side=tk.LEFT, fill='x', expand=True, padx=(5, 5))
        # Use regular tk Button for consistent styling
        tk.Button(bond_file_frame, 
                 text="Browse", 
                 command=lambda: self.browse_file(self.bond_file_var),
                 font=('Helvetica', 11),
                 background=self.colors["primary"],
                 foreground='black',
                 activebackground=self.colors["secondary"],
                 activeforeground='black').pack(side=tk.RIGHT)
        
        # Notes File
        notes_file_frame = ttk.Frame(files_frame)
        notes_file_frame.pack(fill='x', pady=5)
        ttk.Label(notes_file_frame, text="Structured Notes:").pack(side=tk.LEFT)
        self.notes_file_var = tk.StringVar()
        ttk.Entry(notes_file_frame, textvariable=self.notes_file_var).pack(side=tk.LEFT, fill='x', expand=True, padx=(5, 5))
        # Use regular tk Button for consistent styling
        tk.Button(notes_file_frame, 
                 text="Browse", 
                 command=lambda: self.browse_file(self.notes_file_var),
                 font=('Helvetica', 11),
                 background=self.colors["primary"],
                 foreground='black',
                 activebackground=self.colors["secondary"],
                 activeforeground='black').pack(side=tk.RIGHT)
        
        # Output Directory
        ttk.Label(files_frame, text="Output Directory", style="SectionHeader.TLabel").pack(fill='x', pady=(15, 10))
        
        dir_frame = ttk.Frame(files_frame)
        dir_frame.pack(fill='x', pady=5)
        ttk.Label(dir_frame, text="Results Directory:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.output_dir_var).pack(side=tk.LEFT, fill='x', expand=True, padx=(5, 5))
        # Use regular tk Button for consistent styling
        tk.Button(dir_frame, 
                 text="Browse", 
                 command=self.browse_directory,
                 font=('Helvetica', 11),
                 background=self.colors["primary"],
                 foreground='black',
                 activebackground=self.colors["secondary"],
                 activeforeground='black').pack(side=tk.RIGHT)
        
        # Generate Plots
        plot_frame = ttk.Frame(files_frame)
        plot_frame.pack(fill='x', pady=10)
        self.plot_var = tk.BooleanVar()
        ttk.Checkbutton(plot_frame, text="Generate Plots", variable=self.plot_var).pack(side=tk.LEFT)
    
    def create_results_view(self):
        # Create a container frame with sidebar and main content
        container = ttk.Frame(self.results_tab)
        container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create sidebar frame (left side - summary statistics)
        sidebar = ttk.Frame(container, style='Sidebar.TFrame', width=400)  # Increased from 350 to 400
        sidebar.pack(side=tk.LEFT, fill='y', padx=5, pady=5)
        sidebar.pack_propagate(False)  # Don't shrink
        
        # Create content frame (right side - plots)
        content = ttk.Frame(container, style='Content.TFrame')
        content.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        
        # Summary Statistics Section
        summary_frame = ttk.LabelFrame(sidebar, text="Summary Statistics", padding=10)
        summary_frame.pack(fill='x', pady=5, padx=10)
        
        # Create a treeview for summary statistics
        columns = ("Metric", "Traditional", "Structured")
        self.summary_tree = ttk.Treeview(summary_frame, columns=columns, show="headings", height=8)
        self.summary_tree.pack(fill='both', expand=True, pady=5)
        
        # Configure column headings
        self.summary_tree.heading("Metric", text="Metric")
        self.summary_tree.heading("Traditional", text="Traditional")
        self.summary_tree.heading("Structured", text="Structured")
        
        # Configure column widths
        self.summary_tree.column("Metric", width=120, anchor='w')
        self.summary_tree.column("Traditional", width=100, anchor='e')
        self.summary_tree.column("Structured", width=100, anchor='e')
        
        # Buttons to open results folder and refresh
        button_frame = ttk.Frame(sidebar, style='Sidebar.TFrame')
        button_frame.pack(fill='x', pady=10, padx=10)
        
        # Open Results Folder button
        open_folder_button = tk.Button(button_frame, 
                                      text="Open Results Folder", 
                                      command=self.open_results_folder,
                                      font=('Helvetica', 12),
                                      background=self.colors["primary"],
                                      foreground='black',  # Changed from white to black
                                      activebackground=self.colors["secondary"],
                                      activeforeground='black',  # Changed from white to black
                                      padx=10,
                                      pady=5)
        open_folder_button.pack(fill='x', pady=(0, 5))
        
        # Refresh Results button
        refresh_button = tk.Button(button_frame, 
                                   text="Refresh Results", 
                                   command=self.load_results,
                                   font=('Helvetica', 12),
                                   background=self.colors["secondary"],
                                   foreground='black',  # Changed from white to black
                                   activebackground=self.colors["primary"],
                                   activeforeground='black',  # Changed from white to black
                                   padx=10,
                                   pady=5)
        refresh_button.pack(fill='x')
        
        # Plot area
        notebook = ttk.Notebook(content)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs for different plots
        self.portfolio_tab = ttk.Frame(notebook)
        self.returns_tab = ttk.Frame(notebook)
        
        notebook.add(self.portfolio_tab, text="Portfolio Values")
        notebook.add(self.returns_tab, text="Annual Returns")
        
        # Add header to portfolio tab
        ttk.Label(self.portfolio_tab, 
                 text="Portfolio Values Over Time", 
                 style="Header.TLabel").pack(pady=(10, 0))
        
        # Add header to returns tab
        ttk.Label(self.returns_tab, 
                 text="Annual Portfolio Returns", 
                 style="Header.TLabel").pack(pady=(10, 0))
        
        # Add placeholders for plots
        ttk.Label(self.portfolio_tab, 
                 text="Run a simulation to view portfolio values plot",
                 font=('Helvetica', 12, 'italic')).pack(pady=150)
        ttk.Label(self.returns_tab, 
                 text="Run a simulation to view annual returns plot",
                 font=('Helvetica', 12, 'italic')).pack(pady=150)
    
    def set_default_values(self):
        # Set default values based on the README
        self.start_year_var.set("2008")
        self.end_year_var.set("2020")
        self.initial_value_var.set("1000000")
        self.protection_level_var.set("10")
        self.withdrawal_rate_var.set("4")
        self.withdrawal_type_var.set("fixed_percent")
        self.initial_age_var.set("65")
        
        self.trad_sp500_var.set("60")
        self.trad_bonds_var.set("40")
        self.struct_sp500_var.set("40")
        self.struct_bonds_var.set("30")
        self.struct_notes_var.set("30")
        
        # Default file paths - updated to match existing files
        self.sp500_file_var.set("data/sp500_returns.csv")
        self.bond_file_var.set("data/bond_returns.csv")
        self.notes_file_var.set("data/structured_notes.csv")
        self.output_dir_var.set("results")
        
        # Set Generate Plots to checked by default
        self.plot_var.set(True)
    
    def browse_file(self, var):
        filename = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            var.set(filename)
    
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def validate_inputs(self):
        try:
            # Check numerical values
            start_year = int(self.start_year_var.get())
            end_year = int(self.end_year_var.get())
            initial_value = float(self.initial_value_var.get())
            protection_level = float(self.protection_level_var.get()) / 100  # Convert from percentage
            withdrawal_rate = float(self.withdrawal_rate_var.get()) / 100  # Convert from percentage
            
            # Check allocation percentages
            trad_sp500 = float(self.trad_sp500_var.get()) / 100
            trad_bonds = float(self.trad_bonds_var.get()) / 100
            struct_sp500 = float(self.struct_sp500_var.get()) / 100
            struct_bonds = float(self.struct_bonds_var.get()) / 100
            struct_notes = float(self.struct_notes_var.get()) / 100
            
            # Check that allocations sum to 100%
            if not np.isclose(trad_sp500 + trad_bonds, 1.0, atol=0.01):
                messagebox.showerror("Invalid Input", "Traditional portfolio allocations must sum to 100%")
                return False
            
            if not np.isclose(struct_sp500 + struct_bonds + struct_notes, 1.0, atol=0.01):
                messagebox.showerror("Invalid Input", "Structured portfolio allocations must sum to 100%")
                return False
            
            # Check file paths
            for path_var in [self.sp500_file_var, self.bond_file_var, self.notes_file_var]:
                if not os.path.exists(path_var.get()):
                    messagebox.showerror("File Not Found", f"File not found: {path_var.get()}")
                    return False
            
            # Check output directory
            if not os.path.exists(self.output_dir_var.get()):
                # Ask if we should create it
                if messagebox.askyesno("Create Directory", f"Output directory does not exist. Create it?"):
                    os.makedirs(self.output_dir_var.get())
                else:
                    return False
            
            return True
        
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your inputs: {str(e)}")
            return False
    
    def run_simulation(self):
        if not self.validate_inputs():
            return
        
        # Build the command
        cmd = [
            "python3", "run_simulation.py",
            "--start_year", self.start_year_var.get(),
            "--end_year", self.end_year_var.get(),
            "--initial_value", self.initial_value_var.get(),
            "--protection_level", str(float(self.protection_level_var.get()) / 100),
            "--withdrawal_rate", str(float(self.withdrawal_rate_var.get()) / 100),
            "--withdrawal_type", self.withdrawal_type_var.get(),
            "--initial_age", self.initial_age_var.get(),
            "--trad_sp500", str(float(self.trad_sp500_var.get()) / 100),
            "--trad_bonds", str(float(self.trad_bonds_var.get()) / 100),
            "--struct_sp500", str(float(self.struct_sp500_var.get()) / 100),
            "--struct_bonds", str(float(self.struct_bonds_var.get()) / 100),
            "--struct_notes", str(float(self.struct_notes_var.get()) / 100),
            "--sp500_file", self.sp500_file_var.get(),
            "--bond_file", self.bond_file_var.get(),
            "--notes_file", self.notes_file_var.get(),
            "--output_dir", self.output_dir_var.get()
        ]
        
        if self.plot_var.get():
            cmd.append("--plot")
        
        # Run the simulation
        try:
            self.root.config(cursor="wait")
            self.root.update()
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                messagebox.showerror("Simulation Error", f"Error running simulation:\n{result.stderr}")
                self.root.config(cursor="")
                return
            
            # Show success message
            messagebox.showinfo("Success", "Simulation completed successfully!")
            
            # Switch to results tab
            self.notebook.select(self.results_tab)
            
            # Load and display results
            self.load_results()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.root.config(cursor="")
    
    def load_results(self):
        # Find the most recent simulation results
        output_dir = self.output_dir_var.get()
        
        # Look for the most recent files
        results_files = [f for f in os.listdir(output_dir) if f.startswith('simulation_results_')]
        summary_files = [f for f in os.listdir(output_dir) if f.startswith('simulation_summary_')]
        portfolio_plot_files = [f for f in os.listdir(output_dir) if f.startswith('portfolio_values_')]
        returns_plot_files = [f for f in os.listdir(output_dir) if f.startswith('annual_returns_')]
        
        if not results_files or not summary_files:
            messagebox.showwarning("No Results", "No simulation results found in the output directory.")
            return
        
        # Get the most recent files
        results_file = sorted(results_files)[-1]
        summary_file = sorted(summary_files)[-1]
        portfolio_plot = sorted(portfolio_plot_files)[-1] if portfolio_plot_files else None
        returns_plot = sorted(returns_plot_files)[-1] if returns_plot_files else None
        
        # Load summary statistics
        try:
            summary_df = pd.read_csv(os.path.join(output_dir, summary_file))
            
            # Update summary treeview
            self.summary_tree.delete(*self.summary_tree.get_children())
            
            # Extract data for each portfolio type
            trad_data = summary_df[summary_df.iloc[:, 0] == 'traditional'].iloc[0] if 'traditional' in summary_df.iloc[:, 0].values else None
            struct_data = summary_df[summary_df.iloc[:, 0] == 'structured'].iloc[0] if 'structured' in summary_df.iloc[:, 0].values else None
            
            # Add rows for each statistic if we have data
            if trad_data is not None and struct_data is not None:
                # Initial Value
                self.summary_tree.insert('', 'end', values=(
                    'Initial Value', 
                    f"${float(trad_data['initial_value']):,.2f}", 
                    f"${float(struct_data['initial_value']):,.2f}"
                ))
                
                # Final Value
                self.summary_tree.insert('', 'end', values=(
                    'Final Value', 
                    f"${float(trad_data['final_value']):,.2f}", 
                    f"${float(struct_data['final_value']):,.2f}"
                ))
                
                # Total Return
                self.summary_tree.insert('', 'end', values=(
                    'Total Return', 
                    f"{float(trad_data['total_return']):.2%}", 
                    f"{float(struct_data['total_return']):.2%}"
                ))
                
                # CAGR
                self.summary_tree.insert('', 'end', values=(
                    'CAGR', 
                    f"{float(trad_data['cagr']):.2%}", 
                    f"{float(struct_data['cagr']):.2%}"
                ))
                
                # Volatility
                self.summary_tree.insert('', 'end', values=(
                    'Volatility', 
                    f"{float(trad_data['volatility']):.2%}", 
                    f"{float(struct_data['volatility']):.2%}"
                ))
                
                # Max Drawdown
                self.summary_tree.insert('', 'end', values=(
                    'Max Drawdown', 
                    f"{float(trad_data['max_drawdown']):.2%}", 
                    f"{float(struct_data['max_drawdown']):.2%}"
                ))
            
            # Clear existing plots
            for widget in self.portfolio_tab.winfo_children():
                widget.destroy()
            for widget in self.returns_tab.winfo_children():
                widget.destroy()
            
            # Add headers to the tabs
            ttk.Label(self.portfolio_tab, 
                     text="Portfolio Values Over Time", 
                     style="Header.TLabel").pack(pady=(10, 5))
            
            ttk.Label(self.returns_tab, 
                     text="Annual Portfolio Returns", 
                     style="Header.TLabel").pack(pady=(10, 5))
            
            # Display plots if available
            if self.plot_var.get() and portfolio_plot and returns_plot:
                # Portfolio values plot - make it fill the space better
                portfolio_fig = plt.Figure(figsize=(14, 9), dpi=100)
                portfolio_ax = portfolio_fig.add_subplot(111)
                
                # Load and display the image with higher quality
                portfolio_img = plt.imread(os.path.join(output_dir, portfolio_plot))
                portfolio_ax.imshow(portfolio_img, aspect='auto')
                portfolio_ax.axis('off')
                
                # Create canvas for portfolio plot
                portfolio_canvas = FigureCanvasTkAgg(portfolio_fig, master=self.portfolio_tab)
                portfolio_canvas.draw()
                portfolio_canvas_widget = portfolio_canvas.get_tk_widget()
                portfolio_canvas_widget.pack(fill='both', expand=True, padx=5, pady=5)
                
                # Create an interactive toolbar
                from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
                toolbar_frame = tk.Frame(self.portfolio_tab)
                toolbar_frame.pack(fill='x', padx=5)
                toolbar = NavigationToolbar2Tk(portfolio_canvas, toolbar_frame)
                toolbar.update()
                
                # Annual returns plot - make it fill the space better
                returns_fig = plt.Figure(figsize=(14, 9), dpi=100)
                returns_ax = returns_fig.add_subplot(111)
                
                # Load and display the image with higher quality
                returns_img = plt.imread(os.path.join(output_dir, returns_plot))
                returns_ax.imshow(returns_img, aspect='auto')
                returns_ax.axis('off')
                
                # Create canvas for returns plot
                returns_canvas = FigureCanvasTkAgg(returns_fig, master=self.returns_tab)
                returns_canvas.draw()
                returns_canvas_widget = returns_canvas.get_tk_widget()
                returns_canvas_widget.pack(fill='both', expand=True, padx=5, pady=5)
                
                # Create an interactive toolbar
                toolbar_frame = tk.Frame(self.returns_tab)
                toolbar_frame.pack(fill='x', padx=5)
                toolbar = NavigationToolbar2Tk(returns_canvas, toolbar_frame)
                toolbar.update()
                
            else:
                message_style = {'font': ('Helvetica', 14, 'italic'), 'fg': self.colors['primary']}
                ttk.Label(self.portfolio_tab, 
                         text="No plots available. Run simulation with 'Generate Plots' option.",
                         font=('Helvetica', 14, 'italic')).pack(pady=150)
                ttk.Label(self.returns_tab, 
                         text="No plots available. Run simulation with 'Generate Plots' option.",
                         font=('Helvetica', 14, 'italic')).pack(pady=150)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error loading results: {str(e)}")
    
    def open_results_folder(self):
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            # Open the folder in file explorer
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', output_dir])
            else:  # Linux
                subprocess.run(['xdg-open', output_dir])
        else:
            messagebox.showwarning("Not Found", f"Output directory not found: {output_dir}")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioSimulatorGUI(root)
    root.mainloop() 