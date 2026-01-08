from rwanda_housing.wsgi import application
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Export the WSGI app for Vercel
app = application
