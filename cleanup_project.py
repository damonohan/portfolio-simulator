#!/usr/bin/env python3
"""
Portfolio Simulator Cleanup Script

This script cleans up unnecessary files from the Portfolio Simulator project
while preserving all essential components required for the application to function.
"""

import os
import glob
import shutil
import sys

def confirm(prompt):
    """Ask for confirmation before proceeding."""
    response = input(f"{prompt} (y/n): ")
    return response.lower() == 'y'

def cleanup_logs():
    """Remove all log files."""
    log_files = glob.glob('*.log') + glob.glob('*/*.log')
    if not log_files:
        print("No log files found.")
        return
    
    print(f"Found {len(log_files)} log files to remove.")
    for log_file in log_files:
        try:
            os.remove(log_file)
            print(f"Removed: {log_file}")
        except Exception as e:
            print(f"Error removing {log_file}: {e}")

def cleanup_build_artifacts():
    """Remove build artifacts."""
    build_dirs = ['build', 'dist']
    for build_dir in build_dirs:
        if os.path.exists(build_dir):
            try:
                shutil.rmtree(build_dir)
                print(f"Removed directory: {build_dir}")
            except Exception as e:
                print(f"Error removing {build_dir}: {e}")
    
    # Remove spec files
    spec_files = glob.glob('*.spec')
    for spec_file in spec_files:
        try:
            os.remove(spec_file)
            print(f"Removed: {spec_file}")
        except Exception as e:
            print(f"Error removing {spec_file}: {e}")

def cleanup_packaging_experiments():
    """Remove packaging experiment directories."""
    packaging_dirs = [
        'PortfolioSimulator_OneClick',
        'Portfolio_Simulator_Mac'
    ]
    for dir_name in packaging_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Removed directory: {dir_name}")
            except Exception as e:
                print(f"Error removing {dir_name}: {e}")
    
    # Remove packaging ZIP files
    packaging_zips = [
        'PortfolioSimulator_Mac_OneClick.zip'
    ]
    for zip_file in packaging_zips:
        if os.path.exists(zip_file):
            try:
                os.remove(zip_file)
                print(f"Removed: {zip_file}")
            except Exception as e:
                print(f"Error removing {zip_file}: {e}")

def cleanup_pycache():
    """Remove all __pycache__ directories."""
    pycache_dirs = []
    for root, dirs, _ in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_dirs.append(os.path.join(root, dir_name))
    
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            print(f"Removed directory: {pycache_dir}")
        except Exception as e:
            print(f"Error removing {pycache_dir}: {e}")

def cleanup_old_results():
    """Clean up old simulation results while preserving the directory."""
    if os.path.exists('results'):
        # Get all files in the results directory
        results_files = [os.path.join('results', f) for f in os.listdir('results')]
        if results_files:
            print(f"Found {len(results_files)} files in results directory.")
            for file_path in results_files:
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
        else:
            print("Results directory is already empty.")
    else:
        # Create the results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
        print("Created results directory.")

def main():
    """Main execution function."""
    print("Portfolio Simulator Project Cleanup")
    print("===================================")
    print("This script will clean up unnecessary files while preserving essential components.")
    print("The following operations are available:")
    print("1. Remove log files")
    print("2. Remove build artifacts (build/, dist/, *.spec)")
    print("3. Remove packaging experiments")
    print("4. Remove Python cache (__pycache__)")
    print("5. Clean old simulation results")
    print("6. Run all cleanup operations")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-6): ")
    
    if choice == '0':
        print("Exiting without changes.")
        return
    
    if choice == '1' or choice == '6':
        if choice == '6' or confirm("Remove all log files?"):
            cleanup_logs()
    
    if choice == '2' or choice == '6':
        if choice == '6' or confirm("Remove build artifacts?"):
            cleanup_build_artifacts()
    
    if choice == '3' or choice == '6':
        if choice == '6' or confirm("Remove packaging experiments?"):
            cleanup_packaging_experiments()
    
    if choice == '4' or choice == '6':
        if choice == '6' or confirm("Remove Python cache?"):
            cleanup_pycache()
    
    if choice == '5' or choice == '6':
        if choice == '6' or confirm("Clean old simulation results?"):
            cleanup_old_results()
    
    print("\nCleanup completed successfully!")
    print("Essential files and data for the Portfolio Simulator have been preserved.")
    print("The application should continue to function normally.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1) 