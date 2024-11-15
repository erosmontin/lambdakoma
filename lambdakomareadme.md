# lambdaKoma

## Installation

### Step 1: Install Julia
On Windows:
1. [Download Julia](https://julialang.org/downloads/) from the official website.
2. Run the installer and follow the instructions.
3. After installation, add Julia to your system path:
   - Open the Start menu, search for 'Environment Variables,' and select 'Edit the system environment variables.'
   - Click on 'Environment Variables.'
   - Under 'System variables,' find 'Path,' select it, and click 'Edit.'
   - Click 'New' and add the path where Julia was installed (usually C:\Users\YourUsername\AppData\Local\Programs\Julia-1.x.x\bin).
   - Click 'OK' to close the windows.

On Mac:
1. Open the terminal.
2. Install Julia using Homebrew:
   ```
   brew install --cask julia
   ```
4. Verify the installation:
   ```
   julia --version
   ```

On Linux:
1. Open the terminal.
2. Download the latest version of Julia:
   ```
   wget https://julialang-s3.julialang.org/bin/linux/x64/1.9/julia-1.9.0-linux-x86_64.tar.gz
   ```
4. Extract the downloaded file and move it to /opt:
   ```
   tar xzf julia-1.9.0-linux-x86_64.tar.gz
   sudo mv julia-1.9.0 /opt/
   ```
5. Add Julia to your path:
   ```
   sudo ln -s /opt/julia-1.9.0/bin/julia /usr/local/bin/julia
   ```
7. Verify the installation:
   ```
   julia --version
   ```


## Step 2: Install Julia Packages
1. Open Julia in the terminal:
   ```
   julia
   ```
3. Add the necessary packages:
   ```
   using Pkg
   Pkg.add(["KomaMRI", "FileIO", "JLD2","JSON","NPZ","NIfTI"])
   ```
4. Exit Julia:
   ```
   exit()
   ```

## Step 3: Install Python
On Windows:
1. [Download](https://www.python.org/downloads/) and install Python from the official site.
2. During installation, make sure to check the box 'Add Python to PATH.'

On Mac:
1. Open the terminal and install Python via Homebrew:
   ```
   brew install python
   ```

On Linux:
1. Open the terminal and run:
   ```
   sudo apt update
   sudo apt install python3 python3-pip
   ```
   
## Step 4: Install virtualenv and Create a Python Environment Named camrie
1. Open the terminal (or Command Prompt on Windows).
2. Install virtualenv if it’s not installed:
   ```
   pip install virtualenv
   ```
4. Create a new virtual environment named camrie:
   ```
   virtualenv camrie
   ```

## Step 5: Activate the camrie Environment

On Windows:
   ```
   camrie\Scripts\activate
   ```

On Mac/Linux:
   ```
   source camrie/bin/activate
   ```

## Step 6: Install Python Packages from requirements.txt
Once the camrie environment is active, install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Step 7: Verify Installation
1. Ensure that all Julia packages are installed correctly:
   ```
   julia
   using KomaMRI, FileIO, JLD2, JSON,NPZ,NIfTI
   ```
2. Ensure that all Python packages are installed correctly:
   ```
   pip list
   ```

<!-- 
![JuliaPkgVersion](https://img.shields.io/github/v/tag/JuliaLang/julia?label=Julia) -->
