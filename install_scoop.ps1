# Set the execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Download the Scoop installer
Invoke-RestMethod -Uri 'get.scoop.sh' -OutFile 'install.ps1'

# Run the Scoop installer with the specified parameters
.\install.ps1 -RunAsAdmin -ScoopDir 'C:\Scoop'

# Install Python using Scoop
scoop install python

# Get the path where Python is installed using Scoop
$pythonPath = (scoop prefix python).Trim()

# Upgrade pip
& "$pythonPath\python.exe" -m pip install --upgrade pip


# Navigate to the directory containing requirements.txt (if it's not the current directory)
# Set-Location 'path\to\directory\with\requirements.txt'

# Install packages from requirements.txt using pip
& 'C:\Scoop\apps\python\3.11.4\Scripts\pip.exe' install -r 'C:\Users\x0180368905\Desktop\CSR_Report_env\CSR-Report-Crawler\requirements.txt'

scoop install poppler



# Run the main.py script with Python
python 'C:\Users\x0180368905\Desktop\CSR_Report_env\CSR-Report-Crawler\src\main.py'


# Pause at the end to view any potential error messages
Read-Host "Press Enter to exit..."
