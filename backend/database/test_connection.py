#!/usr/bin/env python3
"""
Script de validación de conexión a base de datos y servicios
Verifica que PostgreSQL, Redis y las APIs estén funcionando correctamente.
"""

import os
import sys
import time
import psycopg2
import redis
import requests
import logging
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConnectionTester:
    """Tester de conexiones a servicios"""
    
    def __init__(self):
        """Inicializar el tester con configuraciones de entorno"""
        self.config = {
            'postgres': {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': int(os.getenv('POSTGRES_PORT', '5432')),
                'database': os.getenv('POSTGRES_DB', 'agente_db'),
                'user': os.getenv('POSTGRES_USER', 'postgres'),
                'password': os.getenv('POSTGRES_PASSWORD', 'postgres_secure_password')
            },
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', '6379')),
                'db': int(os.getenv('REDIS_DB', '0')),
                'password': os.getenv('REDIS_PASSWORD', None)
            },
            'api': {
                'backend_url': os.getenv('BACKEND_URL', 'http://localhost:8000'),
                'frontend_url': os.getenv('FRONTEND_URL', 'http://localhost:3000'),
                'prometheus_url': os.getenv('PROMETHEUS_URL', 'http://localhost:9090'),
                'grafana_url': os.getenv('GRAFANA_URL', 'http://localhost:3001')
            }
        }
        
        self.results = {
            'postgres': {'status': 'pending', 'details': {}},
            'redis': {'status': 'pending', 'details': {}},
            'backend_api': {'status': 'pending', 'details': {}},
            'frontend_app': {'status': 'pending', 'details': {}},
            'prometheus': {'status': 'pending', 'details': {}},
            'grafana': {'status': 'pending', 'details': {}},
            'overall': {'status': 'pending', 'details': {}}
        }
    
    def test_postgresql(self) -> bool:
        """Probar conexión a PostgreSQL"""
        logger.info("🐘 Probando conexión a PostgreSQL...")
        
        try:
            # Probar conexión básica
            conn_str = f"host='{self.config['postgres']['host']}' port='{self.config['postgres']['port']}' database='{self.config['postgres']['database']}' user='{self.config['postgres']['user']}' password='{self.config['postgres']['password']}'"
            
            conn = psycopg2.connect(conn_str)
            
            with conn.cursor() as cur:
                # Verificar versión
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                logger.info(f"  ✅ Versión PostgreSQL: {version.split(',')[0]}")
                
                # Verificar extensión pgvector
                cur.execute("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector';")
                has_pgvector = cur.fetchone()[0] > 0
                
                if has_pgvector:
                    logger.info("  ✅ Extensión pgvector: Disponible")
                else:
                    logger.warning("  ⚠️ Extensión pgvector: No encontrada")
                
                # Verificar tablas
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name;
                """)
                tables = [row[0] for row in cur.fetchall()]
                logger.info(f"  ✅ Tablas encontradas: {len(tables)}")
                
                for table in tables:
                    cur.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cur.fetchone()[0]
                    logger.info(f"    - {table}: {count} registros")
                
                # Verificar índices
                cur.execute("""
                    SELECT indexname, tablename 
                    FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND indexname LIKE '%embedding%'
                """)
                vector_indexes = cur.fetchall()
                logger.info(f"  ✅ Índices vectoriales: {len(vector_indexes)}")
                
                self.results['postgres'] = {
                    'status': 'success',
                    'details': {
                        'version': version,
                        'pgvector': has_pgvector,
                        'tables': tables,
                        'table_counts': {table: cur.execute(f"SELECT COUNT(*) FROM {table};") or cur.fetchone()[0] for table in tables}
                    }
                }
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Error PostgreSQL: {e}")
            self.results['postgres'] = {
                'status': 'error',
                'details': {'error': str(e)}
            }
            return False
    
    def test_redis(self) -> bool:
        """Probar conexión a Redis"""
        logger.info("🔴 Probando conexión a Redis...")
        
        try:
            r = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                password=self.config['redis']['password'],
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Probar ping
            response = r.ping()
            logger.info(f"  ✅ Redis ping: {response}")
            
            # Obtener información
            info = r.info()
            logger.info(f"  ✅ Redis versión: {info.get('redis_version', 'N/A')}")
            logger.info(f"  ✅ Memoria usada: {info.get('used_memory_human', 'N/A')}")
            
            # Probar operaciones básicas
            r.set('test_key', 'test_value', ex=10)
            value = r.get('test_key')
            r.delete('test_key')
            
            if value == b'test_value':
                logger.info("  ✅ Operaciones básicas: OK")
            
            self.results['redis'] = {
                'status': 'success',
                'details': {
                    'version': info.get('redis_version'),
                    'memory': info.get('used_memory_human'),
                    'connected_clients': info.get('connected_clients', 0)
                }
            }
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Error Redis: {e}")
            self.results['redis'] = {
                'status': 'error',
                'details': {'error': str(e)}
            }
            return False
    
    def test_http_service(self, name: str, url: str, endpoint: str = None, timeout: int = 10) -> bool:
        """Probar servicio HTTP"""
        try:
            if endpoint:
                test_url = f"{url.rstrip('/')}/{endpoint.lstrip('/')}"
            else:
                test_url = url.rstrip('/')
            
            logger.info(f"🌐 Probando {name} en {test_url}...")
            
            response = requests.get(test_url, timeout=timeout)
            
            if response.status_code == 200:
                logger.info(f"  ✅ {name}: Estado {response.status_code}")
                
                # Probar endpoints específicos
                if 'health' in endpoint.lower() or endpoint is None:
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            logger.info(f"  ✅ Respuesta健康: {data}")
                    except:
                        logger.info(f"  ✅ Respuesta texto: {response.text[:100]}...")
                
                self.results[name.lower().replace(' ', '_')] = {
                    'status': 'success',
                    'details': {
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds()
                    }
                }
                
                return True
            else:
                logger.warning(f"  ⚠️ {name}: Estado {response.status_code}")
                self.results[name.lower().replace(' ', '_')] = {
                    'status': 'warning',
                    'details': {'status_code': response.status_code}
                }
                return False
                
        except Exception as e:
            logger.error(f"  ❌ Error {name}: {e}")
            self.results[name.lower().replace(' ', '_')] = {
                'status': 'error',
                'details': {'error': str(e)}
            }
            return False
    
    def test_all_services(self) -> bool:
        """Probar todos los servicios"""
        logger.info("🔍 Iniciando validación completa de servicios...")
        
        all_success = True
        
        # Probar PostgreSQL
        if not self.test_postgresql():
            all_success = False
        
        # Probar Redis
        if not self.test_redis():
            all_success = False
        
        # Probar servicios HTTP
        services = [
            ('Backend API', self.config['api']['backend_url'], '/health'),
            ('Frontend App', self.config['api']['frontend_url'], None),
            ('Prometheus', self.config['api']['prometheus_url'], '/api/v1/query?query=up'),
            ('Grafana', self.config['api']['grafana_url'], '/api/health')
        ]
        
        for name, url, endpoint in services:
            if not self.test_http_service(name, url, endpoint):
                all_success = False
        
        return all_success
    
    def run_comprehensive_test(self) -> bool:
        """Ejecutar prueba comprehensiva del sistema"""
        logger.info("🚀 Iniciando prueba comprehensiva del sistema...")
        
        # Esperar a que los servicios estén disponibles
        logger.info("⏳ Esperando a que los servicios estén listos...")
        time.sleep(5)
        
        # Ejecutar pruebas
        all_services_ok = self.test_all_services()
        
        # Generar reporte
        self.generate_report(all_services_ok)
        
        return all_services_ok
    
    def generate_report(self, all_services_ok: bool):
        """Generar reporte de resultados"""
        logger.info("\n" + "="*60)
        logger.info("📋 REPORTE DE VALIDACIÓN")
        logger.info("="*60)
        
        # Mostrar resultados por servicio
        for service_name, result in self.results.items():
            if service_name != 'overall':
                status_icon = {
                    'success': '✅',
                    'warning': '⚠️',
                    'error': '❌',
                    'pending': '⏳'
                }.get(result['status'], '❓')
                
                logger.info(f"{status_icon} {service_name.replace('_', ' ').title()}: {result['status'].upper()}")
                
                if result['details']:
                    for key, value in result['details'].items():
                        logger.info(f"    {key}: {value}")
        
        # Resultado general
        logger.info("\n" + "-"*60)
        if all_services_ok:
            logger.info("🎉 ¡TODOS LOS SERVICIOS FUNCIONANDO CORRECTAMENTE!")
            self.results['overall'] = {
                'status': 'success',
                'details': {'message': 'Todos los servicios están operativos'}
            }
        else:
            logger.warning("⚠️ ALGUNOS SERVICIOS TIENEN PROBLEMAS")
            self.results['overall'] = {
                'status': 'partial',
                'details': {'message': 'Algunos servicios no están disponibles'}
            }
        
        logger.info("="*60)
    
    def interactive_test(self):
        """Ejecutar prueba interactiva con menú"""
        logger.info("🎮 Iniciando prueba interactiva...")
        
        while True:
            print("\n" + "="*50)
            print("🧪 TESTER DE CONEXIONES")
            print("="*50)
            print("1. Probar PostgreSQL")
            print("2. Probar Redis")
            print("3. Probar Backend API")
            print("4. Probar Frontend")
            print("5. Probar Prometheus")
            print("6. Probar Grafana")
            print("7. Prueba completa")
            print("8. Salir")
            print("-"*50)
            
            try:
                choice = input("Selecciona una opción (1-8): ").strip()
                
                if choice == '1':
                    self.test_postgresql()
                elif choice == '2':
                    self.test_redis()
                elif choice == '3':
                    self.test_http_service('Backend API', self.config['api']['backend_url'], '/health')
                elif choice == '4':
                    self.test_http_service('Frontend App', self.config['api']['frontend_url'])
                elif choice == '5':
                    self.test_http_service('Prometheus', self.config['api']['prometheus_url'])
                elif choice == '6':
                    self.test_http_service('Grafana', self.config['api']['grafana_url'])
                elif choice == '7':
                    self.run_comprehensive_test()
                elif choice == '8':
                    logger.info("👋 ¡Hasta luego!")
                    break
                else:
                    logger.warning("⚠️ Opción no válida")
                    
            except KeyboardInterrupt:
                logger.info("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")

def main():
    """Función principal"""
    try:
        tester = ConnectionTester()
        
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == 'postgres':
                success = tester.test_postgresql()
            elif command == 'redis':
                success = tester.test_redis()
            elif command == 'api':
                success = tester.test_http_service('Backend API', tester.config['api']['backend_url'], '/health')
            elif command == 'full' or command == 'comprehensive':
                success = tester.run_comprehensive_test()
            elif command == 'interactive':
                tester.interactive_test()
                return 0
            else:
                logger.info("Uso: python test_connection.py [postgres|redis|api|full|interactive]")
                return 1
                
            return 0 if success else 1
        else:
            # Prueba completa por defecto
            success = tester.run_comprehensive_test()
            return 0 if success else 1
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Prueba cancelada por el usuario")
        return 1
    except Exception as e:
        logger.error(f"💥 Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit(main())