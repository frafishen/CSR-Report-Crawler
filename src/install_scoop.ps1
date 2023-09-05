# Set the execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Get the passed bat directory from the argument
$batDirectory = $args[0]

# Remove the trailing backslash if it exists
$batDirectory = $batDirectory.TrimEnd('\')

# Now continue with your existing code
$absoluteRequirementsPath = Join-Path -Path $batDirectory -ChildPath "src/requirements.txt"
$absoluteMainPath = Join-Path -Path $batDirectory -ChildPath "src/main.py"

# Print the values
Write-Host "Bat Directory: $batDirectory"
Write-Host "Absolute Requirements Path: $absoluteRequirementsPath"
Write-Host "Absolute Main Path: $absoluteMainPath"

# Pause execution
# Read-Host "Press Enter to continue..."

# Download the Scoop installer
Invoke-RestMethod -Uri 'get.scoop.sh' -OutFile 'install.ps1'

# Run the Scoop installer with the specified parameters
& .\install.ps1 -RunAsAdmin -ScoopDir 'C:\Scoop'

# Install Python using Scoop
scoop install python

# Get the path where Python is installed using Scoop
$pythonPath = (scoop prefix python).Trim()

# Upgrade pip
& "$pythonPath\python.exe" -m pip install --upgrade pip

scoop install poppler

# Navigate to the directory containing requirements.txt (if it's not the current directory)
# Set-Location 'path\to\directory\with\requirements.txt'

# Install packages from requirements.txt using pip
# Convert requirements.txt relative path to absolute path
& "$pythonPath\Scripts\pip.exe" install -r $absoluteRequirementsPath

# Run the main.py script with Python
& "$pythonPath\python.exe" $absoluteMainPath



# Pause at the end to view any potential error messages
Read-Host "Press Enter to exit..."
