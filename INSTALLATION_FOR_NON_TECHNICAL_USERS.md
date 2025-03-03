# HALO Portfolio Simulator - Installation Guide for Non-Technical Users

This guide will walk you through installing and running the HALO Portfolio Simulator step-by-step, with minimal technical knowledge required.

## Quick Start (Fully Automated Installation)

Our automated scripts now handle everything for you, including installing Python!

### For Windows:
1. Extract the ZIP file that was shared with you
2. Double-click the file named `install_and_run.bat` 
3. Wait for the installation to complete (this may take a few minutes)
4. The Portfolio Simulator will launch automatically

### For Mac:
1. Extract the ZIP file that was shared with you
2. Right-click on `install_and_run.sh` and select "Open"
3. If you get a security warning, click "Open" to proceed
4. You may be asked for your password (this is needed to install Python)
5. Wait for the installation to complete (this may take a few minutes)
6. The Portfolio Simulator will launch automatically

## If You Encounter Issues

If the automated installation doesn't work, you can try the manual steps below.

## Manual Installation Steps

### Step 1: Install Python (One-Time Setup)

#### For Windows:
1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. **IMPORTANT**: During installation, check the box that says "Add Python to PATH"
3. Click "Install Now"

#### For Mac:
1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Open the downloaded file and follow the installation instructions
3. Complete the installation

### Step 2: Open Command Prompt / Terminal

#### For Windows:
1. Press the Windows key + R
2. Type `cmd` and press Enter
3. A black window will open - this is the command prompt

#### For Mac:
1. Press Command + Space to open Spotlight
2. Type `Terminal` and press Enter
3. A terminal window will open

### Step 3: Navigate to the Portfolio Simulator Folder

Type the following command, replacing `[PATH_TO_FOLDER]` with the actual path where you extracted the files:

#### For Windows:
```
cd [PATH_TO_FOLDER]\portfolio_simulator
```

#### For Mac:
```
cd [PATH_TO_FOLDER]/portfolio_simulator
```

For example, if you extracted it to your Documents folder:
- Windows: `cd C:\Users\YourUsername\Documents\portfolio_simulator`
- Mac: `cd ~/Documents/portfolio_simulator`

### Step 4: Set Up the Environment

Copy and paste these commands one at a time:

#### For Windows:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### For Mac:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Wait for each command to complete before running the next one. The last command will take a few minutes to finish.

### Step 5: Run the Portfolio Simulator

Type this command:

#### For Windows:
```
python gui.py
```

#### For Mac:
```
python gui.py
```

The Portfolio Simulator should now open in a new window!

## Having Trouble?

If you encounter any issues, please:
1. Take a screenshot of any error messages
2. Note which step you were on
3. Contact the person who sent you this file

## Running the Simulator Again Later

To run the simulator again in the future:

### Using the Easy Method:
Simply double-click the same file you used for installation:
- Windows: `install_and_run.bat`
- Mac: `install_and_run.sh`

### Using the Manual Method:
#### For Windows:
1. Open Command Prompt
2. Navigate to the portfolio simulator folder: `cd [PATH_TO_FOLDER]\portfolio_simulator`
3. Activate the environment: `.venv\Scripts\activate`
4. Run the simulator: `python gui.py`

#### For Mac:
1. Open Terminal
2. Navigate to the portfolio simulator folder: `cd [PATH_TO_FOLDER]/portfolio_simulator`
3. Activate the environment: `source .venv/bin/activate`
4. Run the simulator: `python gui.py` 