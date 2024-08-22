#!/usr/bin/env fish

# Activate the virtual environment or create it if it doesn't exist
if not test -d ".venv"
   echo "Virtual environment not found. Creating it now..."
   python3 -m venv .venv
end

# Activate the virtual environment
source .venv/bin/activate.fish

pip install -r requirements.txt


echo ========================START========================

# Pass all arguments to the python script main.py
python3 ghrc.py $argv