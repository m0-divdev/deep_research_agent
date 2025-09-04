#!/usr/bin/env python3
"""Simple startup script for the Deep Research Multi-Agent System."""

import os
import sys
import asyncio
from dotenv import load_dotenv

def check_environment():
    """Check if required environment variables are set."""
    load_dotenv()
    
    required_vars = ["PARALLEL_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file.")
        print("Copy .env.example to .env and fill in your API keys.")
        return False
    
    print("✅ Environment variables configured")
    return True

def main():
    """Main startup function."""
    print("🚀 Deep Research Multi-Agent System")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Import and run the main application
    try:
        import uvicorn
        from config import settings
        
        print(f"🌐 Starting server on {settings.host}:{settings.port}")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/health")
        print("📊 System Status: http://localhost:8000/status")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
