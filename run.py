#!/usr/bin/env python3
"""
ZohoPulse Server Launcher
Runs the FastAPI Zoho CRM Automation Engine on port 8090.
"""

import sys
import os
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("==================================================================")
    print(" Starting ZohoPulse - Intelligent Zoho CRM & Books Automation Suite")
    print(" Running on: http://localhost:8090")
    print(" Deluge Studio: http://localhost:8090/deluge-studio")
    print(" API Console: http://localhost:8090/api-console")
    print(" Architecture & Docs: http://localhost:8090/architecture")
    print("==================================================================")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8090, reload=False, log_level="info")
