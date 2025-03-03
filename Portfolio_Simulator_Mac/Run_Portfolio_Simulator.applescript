#!/usr/bin/osascript

-- Portfolio Simulator Installer and Launcher
-- This script automates the installation and running of Portfolio Simulator

on run
	set scriptPath to (path to me)
	set appFolder to container of scriptPath as text
	
	display dialog "Welcome to Portfolio Simulator!" & return & return & "This script will set up everything you need and launch the application." buttons {"Cancel", "Continue"} default button "Continue" with title "Portfolio Simulator Setup" with icon note
	
	-- Check if Python is installed
	try
		do shell script "which python3"
		set pythonInstalled to true
	on error
		set pythonInstalled to false
	end try
	
	if not pythonInstalled then
		display dialog "Python 3 is required but not found on your system." & return & return & "Please install Python 3 from python.org first, then run this script again." buttons {"OK"} default button "OK" with title "Python Required" with icon caution
		do shell script "open https://www.python.org/downloads/"
		return
	end if
	
	-- Create a virtual environment and install dependencies
	display dialog "Setting up the environment. This may take a few minutes..." buttons {"Cancel", "Continue"} default button "Continue" with title "Portfolio Simulator Setup" with icon note
	
	try
		-- Extract the ZIP file if it exists
		do shell script "cd " & quoted form of POSIX path of appFolder & " && unzip -o -q portfolio_simulator_files.zip -d ."
		
		-- Create virtual environment and install dependencies
		do shell script "cd " & quoted form of POSIX path of appFolder & " && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
		
		-- Run the application
		display dialog "Setup complete! Starting Portfolio Simulator..." buttons {"OK"} default button "OK" with title "Portfolio Simulator" with icon note
		do shell script "cd " & quoted form of POSIX path of appFolder & " && source .venv/bin/activate && python gui.py"
		
	on error errMsg
		display dialog "An error occurred: " & errMsg buttons {"OK"} default button "OK" with title "Setup Error" with icon stop
	end try
end run 