# This is a wrapper for Streamlit Cloud deployment
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set API URL to local for cloud deployment
os.environ['API_URL'] = 'http://localhost:8000'

# Import and run the main UI
from app.ui import *
