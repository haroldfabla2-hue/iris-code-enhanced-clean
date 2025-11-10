"""
Herramienta para ejecución segura de código Python.
Implementa sandboxing y restricciones de seguridad para prevenir ejecución maliciosa.
"""

import sys
import io
import ast
import traceback
import signal
import time
import contextlib
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from threading import Timer

from .base_tool import BaseTool, ToolResult

@dataclass
class ExecutionContext:
    """Contexto de ejecución con variables y restricciones"""
    variables: Dict[str, Any]
    allowed_builtins: List[str]
    forbidden_modules: List[str]
    max_iterations: int = 1000
    max_recursion_depth: int = 3

class SafeExecutionError(Exception):
    """Error específico para ejecución segura"""
    pass

class PythonExecutor(BaseTool):
    """Ejecutor seguro de código Python con restricciones"""
    
    def __init__(self):
        super().__init__(
            name="python_executor",
            description="Ejecutor seguro de código Python con restricciones de sandboxing",
            timeout=60
        )
        
        # Módulos peligrosos que están siempre prohibidos
        self.global_forbidden_modules = [
            'os', 'sys', 'subprocess', 'pickle', 'marshal', 'code',
            'compileall', 'py_compile', 'traceback', 'inspect',
            'tempfile', 'shutil', 'glob', 'fnmatch', 'io', 'fileinput',
            'cProfile', 'pstats', 'profile', 'timeit', 'faulthandler',
            'atexit', 'gc', 'weakref', 'mmap', 'readline', 'rlcompleter',
            'cmd', 'bdb', 'pdb', 'tabnanny', 'checker', 'pyclbr',
            'distutils', 'ensurepip', 'venv', 'zipapp', 'zipfile',
            'tarfile', 'gzip', 'bz2', 'lzma', 'zipimport'
        ]
        
        # Builtins permitidos (lista conservativa)
        self.default_allowed_builtins = [
            # Tipos básicos
            'int', 'float', 'str', 'bool', 'list', 'dict', 'tuple', 'set', 'frozenset',
            'type', 'isinstance', 'issubclass',
            
            # Funciones matemáticas
            'abs', 'min', 'max', 'sum', 'pow', 'round', 'divmod',
            
            # Funciones de secuencia
            'len', 'range', 'enumerate', 'zip', 'reversed', 'sorted',
            
            # Funciones de iteración
            'all', 'any', 'filter', 'map',
            
            # Funciones de cadena
            'str', 'repr', 'format', 'ascii',
            
            # Utilidades
            'print', 'help',
            
            # Funciones de archivo básicas (solo lectura)
            'open'
        ]
        
        # Variables globales seguras por defecto
        self.safe_globals = {
            '__builtins__': self._create_safe_builtins(),
            '__name__': '__main__'
        }
        
        # Variables locales por defecto
        self.safe_locals = {}
    
    def _create_safe_builtins(self) -> Dict[str, Any]:
        """Crea un diccionario de builtins seguros"""
        safe_builtins = {}
        
        for builtin_name in self.default_allowed_builtins:
            if hasattr(__builtins__, builtin_name):
                safe_builtins[builtin_name] = getattr(__builtins__, builtin_name)
        
        # Restringir la función open para solo lectura
        original_open = safe_builtins.get('open')
        if original_open:
            def safe_open(*args, **kwargs):
                # Solo permitir modo de lectura
                if len(args) >= 2:
                    mode = args[1]
                    if mode not in ('r', 'rb', 'rt'):
                        raise SafeExecutionError(f"Modo de archivo no permitido: {mode}")
                elif 'mode' in kwargs:
                    mode = kwargs['mode']
                    if mode not in ('r', 'rb', 'rt'):
                        raise SafeExecutionError(f"Modo de archivo no permitido: {mode}")
                
                return original_open(*args, **kwargs)
            
            safe_builtins['open'] = safe_open
        
        return safe_builtins
    
    def _check_ast_safety(self, code: str) -> List[str]:
        """
        Analiza el AST del código para detectar patrones peligrosos
        
        Args:
            code: Código Python a analizar
            
        Returns:
            Lista de advertencias de seguridad
        """
        warnings = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            warnings.append(f"Error de sintaxis: {e}")
            return warnings
        
        class SecurityVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    name = alias.name
                    if name in self.forbidden_modules:
                        warnings.append(f"Import prohibido: {name}")
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module and node.module in self.forbidden_modules:
                    warnings.append(f"Import from prohibido: {node.module}")
                self.generic_visit(node)
            
            def visit_Call(self, node):
                if hasattr(node.func, 'id'):
                    func_name = node.func.id
                    if func_name in ['exec', 'eval', 'compile']:
                        warnings.append(f"Llamada peligrosa: {func_name}")
                
                # Verificar acceso a atributos peligrosos
                if hasattr(node.func, 'attr'):
                    attr = node.func.attr
                    if attr in ['__globals__', '__locals__', '__import__']:
                        warnings.append(f"Acceso a atributo peligroso: __globals__")
                
                self.generic_visit(node)
            
            def visit_Attribute(self, node):
                attr = node.attr
                if attr.startswith('__') and attr.endswith('__'):
                    if attr in ['__import__', '__globals__', '__locals__', '__code__', '__closure__']:
                        warnings.append(f"Atributo mágico peligroso: {attr}")
                
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                # Verificar nombre de función
                if node.name.startswith('__'):
                    warnings.append(f"Nombre de función prohibido: {node.name}")
                self.generic_visit(node)
        
        visitor = SecurityVisitor()
        visitor.forbidden_modules = self.global_forbidden_modules
        visitor.warnings = warnings
        visitor.visit(tree)
        
        return warnings
    
    def _execute_with_timeout(self, code: str, globals_dict: Dict, locals_dict: Dict, timeout: int) -> tuple:
        """
        Ejecuta código con timeout usando señal
        
        Args:
            code: Código a ejecutar
            globals_dict: Diccionario global
            locals_dict: Diccionario local
            timeout: Timeout en segundos
            
        Returns:
            Tuple (resultado, output, error)
        """
        result = None
        output = ""
        error = None
        
        def timeout_handler():
            raise TimeoutError(f"Ejecución excedió {timeout} segundos")
        
        # Configurar timeout
        timer = Timer(timeout, timeout_handler)
        
        try:
            timer.start()
            
            # Capturar stdout
            captured_output = io.StringIO()
            
            # Ejecutar código en contexto controlado
            with contextlib.redirect_stdout(captured_output):
                result = exec(code, globals_dict, locals_dict)
            
            output = captured_output.getvalue()
            
        except TimeoutError:
            error = f"Timeout: El código tardó más de {timeout} segundos"
        except Exception as e:
            error = f"Error en ejecución: {str(e)}\n{traceback.format_exc()}"
        finally:
            timer.cancel()
        
        return result, output, error
    
    def execute_code(self, code: str, context: Optional[ExecutionContext] = None,
                    timeout: Optional[int] = None) -> ToolResult:
        """
        Ejecuta código Python de forma segura
        
        Args:
            code: Código Python a ejecutar
            context: Contexto de ejecución personalizado
            timeout: Timeout personalizado
            
        Returns:
            ToolResult con el resultado de la ejecución
        """
        self.set_running()
        
        try:
            # Usar timeout personalizado o el de la herramienta
            execution_timeout = timeout or self.timeout
            
            # Sanitizar código
            sanitized_code = self.sanitize_input(code, max_length=10000)
            
            # Validaciones básicas
            if not sanitized_code.strip():
                return self.create_result(
                    success=False,
                    error="Código vacío"
                )
            
            # Verificar longitud
            if len(sanitized_code) > 10000:
                return self.create_result(
                    success=False,
                    error="Código demasiado largo (máximo 10000 caracteres)"
                )
            
            # Análisis AST de seguridad
            security_warnings = self._check_ast_safety(sanitized_code)
            if security_warnings:
                self.logger.warning(f"Advertencias de seguridad detectadas: {security_warnings}")
                # Continuar pero loggear las advertencias
            
            # Configurar contexto de ejecución
            if context is None:
                context = ExecutionContext(
                    variables={},
                    allowed_builtins=self.default_allowed_builtins,
                    forbidden_modules=self.global_forbidden_modules
                )
            
            # Preparar diccionarios de ejecución
            exec_globals = self.safe_globals.copy()
            exec_locals = self.safe_locals.copy()
            
            # Asegurar print disponible
            exec_globals['print'] = print
            
            # Agregar variables del contexto
            exec_globals.update(context.variables)
            
            # Ejecutar código con timeout
            start_time = time.time()
            result, output, error = self._execute_with_timeout(
                sanitized_code, exec_globals, exec_locals, execution_timeout
            )
            
            execution_time = time.time() - start_time
            
            if error:
                self.set_failed(error)
                return self.create_result(
                    success=False,
                    error=error,
                    execution_time=execution_time
                )
            
            # Preparar resultado
            result_data = {
                'result': result,
                'output': output.strip() if output else '',
                'locals': dict(exec_locals),
                'execution_time': execution_time,
                'code_length': len(sanitized_code),
                'security_warnings': security_warnings
            }
            
            self.set_completed()
            
            return self.create_result(
                success=True,
                data=result_data,
                execution_time=execution_time,
                output_lines=len(output.splitlines()) if output else 0
            )
            
        except Exception as e:
            return self.handle_exception(e)
    
    def execute_function(self, function_code: str, function_name: str, 
                        args: Optional[Dict[str, Any]] = None, 
                        **kwargs) -> ToolResult:
        """
        Ejecuta una función específica de forma segura
        
        Args:
            function_code: Código que define la función
            function_name: Nombre de la función a ejecutar
            args: Argumentos para la función
            **kwargs: Argumentos adicionales
            
        Returns:
            ToolResult con el resultado de la función
        """
        try:
            # Ejecutar definición de función
            exec_result = self.execute_code(function_code)
            
            if not exec_result.success:
                return exec_result
            
            # Construir código de llamada
            call_code = f"{function_name}("
            
            if args:
                arg_strings = [f"{k}={repr(v)}" for k, v in args.items()]
                call_code += ", ".join(arg_strings)
            
            call_code += ")"
            
            # Ejecutar llamada
            call_result = self.execute_code(call_code)
            
            return call_result
            
        except Exception as e:
            return self.handle_exception(e)
    
    def test_code_safety(self, code: str) -> ToolResult:
        """
        Prueba la seguridad del código sin ejecutarlo
        
        Args:
            code: Código a analizar
            
        Returns:
            ToolResult con análisis de seguridad
        """
        try:
            # Sanitizar código
            sanitized_code = self.sanitize_input(code, max_length=10000)
            
            # Análisis AST
            security_warnings = self._check_ast_safety(sanitized_code)
            
            # Análisis sintáctico
            try:
                ast.parse(sanitized_code)
                syntax_ok = True
                syntax_error = None
            except SyntaxError as e:
                syntax_ok = False
                syntax_error = str(e)
            
            # Análisis de complejidad básica
            complexity_metrics = {
                'lines': len(sanitized_code.splitlines()),
                'characters': len(sanitized_code),
                'nesting_level': self._calculate_nesting_level(sanitized_code),
                'function_count': sanitized_code.count('def '),
                'class_count': sanitized_code.count('class '),
                'import_count': sanitized_code.count('import ')
            }
            
            self.set_completed()
            
            return self.create_result(
                success=True,
                data={
                    'syntax_valid': syntax_ok,
                    'syntax_error': syntax_error,
                    'security_warnings': security_warnings,
                    'safety_score': self._calculate_safety_score(security_warnings),
                    'complexity_metrics': complexity_metrics
                },
                code_analysis=True
            )
            
        except Exception as e:
            return self.handle_exception(e)
    
    def _calculate_nesting_level(self, code: str) -> int:
        """Calcula el nivel máximo de anidamiento en el código"""
        max_nesting = 0
        current_nesting = 0
        
        for char in code:
            if char == '{' or char == '(' or char == '[':
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif char == '}' or char == ')' or char == ']':
                current_nesting -= 1
        
        return max_nesting
    
    def _calculate_safety_score(self, warnings: List[str]) -> float:
        """Calcula una puntuación de seguridad (0-100)"""
        if not warnings:
            return 100.0
        
        # Reducir puntuación por cada advertencia
        penalty_per_warning = 10.0
        return max(0.0, 100.0 - len(warnings) * penalty_per_warning)
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Ejecuta la funcionalidad principal del ejecutor Python
        
        Args:
            **kwargs: Argumentos que pueden incluir:
                - code: Código a ejecutar
                - function_code: Código de función
                - function_name: Nombre de función
                - args: Argumentos para la función
                - operation: tipo de operación ('execute', 'test_safety', 'execute_function')
                - timeout: timeout personalizado
                
        Returns:
            ToolResult con el resultado de la operación
        """
        operation = kwargs.get('operation', 'execute')
        
        if operation == 'test_safety':
            code = kwargs.get('code')
            if not code:
                return self.create_result(
                    success=False,
                    error="Código requerido para análisis de seguridad"
                )
            return self.test_code_safety(code)
        
        elif operation == 'execute_function':
            function_code = kwargs.get('function_code')
            function_name = kwargs.get('function_name')
            args = kwargs.get('args', {})
            
            if not function_code or not function_name:
                return self.create_result(
                    success=False,
                    error="Código de función y nombre requeridos"
                )
            
            return self.execute_function(function_code, function_name, args, **kwargs)
        
        elif operation == 'execute':
            code = kwargs.get('code')
            if not code:
                return self.create_result(
                    success=False,
                    error="Código requerido para ejecutar"
                )
            
            timeout = kwargs.get('timeout')
            return self.execute_code(code, timeout=timeout)
        
        else:
            return self.create_result(
                success=False,
                error=f"Operación no reconocida: {operation}"
            )