#!/usr/bin/env python3
"""
Servidor rápido que ejecuta el main.py completo para pruebas de assets
"""
import uvicorn
import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación principal
from main import app

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    )