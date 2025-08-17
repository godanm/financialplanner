#!/usr/bin/env python3
"""
Financial Planner Application Runner
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set environment variables
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"

def main():
    """Main function to run the Streamlit app"""
    
    # Import and run the app
    import subprocess
    
    app_file = src_path / "app.py"
    
    if not app_file.exists():
        print("❌ app.py not found in src directory")
        sys.exit(1)
    
    try:
        print("🚀 Starting Financial Planner Application...")
        print("📍 Open your browser to: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the application")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_file),
            "--server.port=8501",
            "--server.address=localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
