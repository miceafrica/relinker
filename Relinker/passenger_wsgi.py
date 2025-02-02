import sys
import os
from app import app as application  # app is your Flask instance

# Add the project directory to the system path
sys.path.insert(0, os.path.dirname(__file__))
