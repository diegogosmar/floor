"""
ANS: Agent Name Server - Standalone application entry point

Run: uvicorn src.ans.main:app --port 8001
"""

import uvicorn
from src.ans.server import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

