#!/usr/bin/env python3
"""
Script de prueba para verificar importaciones
"""
print("Iniciando pruebas de importación...")

try:
    print("1. Probando FastAPI...")
    import fastapi
    print("   ✅ FastAPI importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando FastAPI: {e}")

try:
    print("2. Probando PyTorch...")
    import torch
    print(f"   ✅ PyTorch importado correctamente (versión {torch.__version__})")
except ImportError as e:
    print(f"   ❌ Error importando PyTorch: {e}")

try:
    print("3. Probando sentence-transformers...")
    import sentence_transformers
    print("   ✅ sentence-transformers importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando sentence-transformers: {e}")

try:
    print("4. Probando SQLAlchemy...")
    import sqlalchemy
    print(f"   ✅ SQLAlchemy importado correctamente (versión {sqlalchemy.__version__})")
except ImportError as e:
    print(f"   ❌ Error importando SQLAlchemy: {e}")

try:
    print("5. Probando psycopg2...")
    import psycopg2
    print("   ✅ psycopg2 importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando psycopg2: {e}")

try:
    print("6. Probando embedding_service...")
    from app.services.embedding_service import EmbeddingService
    print("   ✅ embedding_service importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando embedding_service: {e}")

try:
    print("7. Probando chunking_service...")
    from app.services.chunking_service import DocumentChunker
    print("   ✅ chunking_service importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando chunking_service: {e}")

print("\nPruebas completadas.")