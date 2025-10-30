# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate   # macOS / Linux
# On Windows: venv\Scripts\activate

# 3. Install packages inside the venv
pip install --upgrade openai python-dotenv

# 4. Run your script inside this venv
python agent.py
