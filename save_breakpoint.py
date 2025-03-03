#!/usr/bin/env python3
"""
Save Breakpoint Script

This script helps save your current progress by creating a Git repository (if one doesn't exist)
and committing the current state with a meaningful message. It also provides options to create
branches for different development paths or versions.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

def run_command(command):
    """Run a shell command and return the result."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def check_git_installed():
    """Check if Git is installed."""
    _, exit_code = run_command("git --version")
    return exit_code == 0

def check_git_repo():
    """Check if current directory is a Git repo."""
    _, exit_code = run_command("git rev-parse --is-inside-work-tree")
    return exit_code == 0

def init_git_repo():
    """Initialize a new Git repository."""
    print("Initializing Git repository...")
    run_command("git init")
    
    # Create a basic .gitignore file
    with open(".gitignore", "w") as f:
        f.write("# Python specific\n")
        f.write("__pycache__/\n")
        f.write("*.py[cod]\n")
        f.write("*$py.class\n")
        f.write("*.so\n")
        f.write(".Python\n")
        f.write("env/\n")
        f.write("build/\n")
        f.write("develop-eggs/\n")
        f.write("dist/\n")
        f.write("downloads/\n")
        f.write("eggs/\n")
        f.write(".eggs/\n")
        f.write("lib/\n")
        f.write("lib64/\n")
        f.write("parts/\n")
        f.write("sdist/\n")
        f.write("var/\n")
        f.write("*.egg-info/\n")
        f.write(".installed.cfg\n")
        f.write("*.egg\n\n")
        
        f.write("# Virtual environments\n")
        f.write(".env\n")
        f.write(".venv\n")
        f.write("venv/\n")
        f.write("ENV/\n\n")
        
        f.write("# OS specific files\n")
        f.write(".DS_Store\n")
        f.write(".DS_Store?\n")
        f.write("._*\n")
        f.write(".Spotlight-V100\n")
        f.write(".Trashes\n")
        f.write("ehthumbs.db\n")
        f.write("Thumbs.db\n\n")
        
        f.write("# Log files\n")
        f.write("*.log\n")
    
    # Add README.md if it doesn't exist
    if not os.path.exists("README.md"):
        with open("README.md", "w") as f:
            f.write("# HALO Portfolio Simulator\n\n")
            f.write("A GUI application for simulating investment portfolios with structured notes.\n\n")
            f.write("## Setup\n\n")
            f.write("1. Clone this repository\n")
            f.write("2. Install requirements: `pip install -r requirements.txt`\n")
            f.write("3. Run the application: `python run_gui.py`\n\n")
            f.write("## Features\n\n")
            f.write("- Simulate traditional and structured portfolios\n")
            f.write("- Compare performance metrics\n")
            f.write("- Visualize results with interactive charts\n")
            f.write("- Configure portfolio allocations and parameters\n")
    
    print("Git repository initialized with .gitignore and README.md")

def save_breakpoint(message, branch=None):
    """Save current state in Git."""
    # Add all files
    run_command("git add .")
    
    # Create a commit with the provided message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"{message} - {timestamp}"
    run_command(f'git commit -m "{full_message}"')
    
    # Create a new branch if requested
    if branch:
        run_command(f"git branch {branch}")
        run_command(f"git checkout {branch}")
        print(f"Created and switched to branch: {branch}")
    
    # Get the commit hash for reference
    commit_hash, _ = run_command("git rev-parse HEAD")
    
    print(f"Breakpoint saved: {full_message}")
    print(f"Commit: {commit_hash[:10]}")

def main():
    parser = argparse.ArgumentParser(description="Save your current progress as a Git commit.")
    parser.add_argument("message", help="Commit message describing this breakpoint")
    parser.add_argument("--branch", "-b", help="Create a new branch at this point")
    
    args = parser.parse_args()
    
    # Check if Git is installed
    if not check_git_installed():
        print("Error: Git is not installed or not in your PATH.")
        print("Please install Git from https://git-scm.com/ and try again.")
        sys.exit(1)
    
    # Check if we're in a Git repository
    if not check_git_repo():
        print("This directory is not a Git repository.")
        choice = input("Would you like to initialize a new Git repository? (y/n): ")
        if choice.lower() == 'y':
            init_git_repo()
        else:
            print("Aborted. No changes were made.")
            sys.exit(0)
    
    # Save the breakpoint
    save_breakpoint(args.message, args.branch)
    
    print("\nNext steps:")
    print("1. To share this project with others, create a remote repository on GitHub or similar service.")
    print("2. Link this repository with: git remote add origin YOUR_REPO_URL")
    print("3. Push your changes with: git push -u origin main")

if __name__ == "__main__":
    main() 