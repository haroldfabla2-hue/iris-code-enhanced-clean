#!/usr/bin/env node
/**
 * Script de testing de integración IRIS Code
 * Prueba la conectividad entre frontend y backend
 */

const API_BASE = 'http://localhost:8001';
const FRONTEND_URL = 'http://localhost:3001';

const tests = [
    {
        name: 'Health Check',
        endpoint: '/health',
        method: 'GET'
    },
    {
        name: 'Root Endpoint', 
        endpoint: '/',
        method: 'GET'
    },
    {
        name: 'Phase 1 Status',
        endpoint: '/api/v1/fase1-status',
        method: 'GET'
    },
    {
        name: 'Frontend Server',
        endpoint: '/',
        url: FRONTEND_URL,
        method: 'GET'
    }
];

// Colores para la consola
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m',
    bold: '\x1b[1m'
};

console.log(`${colors.bold}${colors.blue}🚀 INICIANDO PRUEBAS DE INTEGRACIÓN IRIS CODE${colors.reset}`);
console.log(`${colors.blue}==================================================${colors.reset}\n`);

async function runTest(test) {
    const url = test.url || `${API_BASE}${test.endpoint}`;
    
    try {
        console.log(`${colors.blue}🔍 Probando: ${test.name}...${colors.reset}`);
        console.log(`   URL: ${url}`);
        
        const response = await fetch(url, {
            method: test.method,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log(`   ${colors.green}✅ ÉXITO - Status: ${response.status}${colors.reset}`);
            console.log(`   ${colors.green}📄 Respuesta: ${JSON.stringify(data, null, 2).substring(0, 200)}...${colors.reset}`);
            return { success: true, data, status: response.status };
        } else {
            console.log(`   ${colors.red}❌ FALLO - Status: ${response.status}${colors.reset}`);
            return { success: false, status: response.status };
        }
    } catch (error) {
        console.log(`   ${colors.red}❌ ERROR - ${error.message}${colors.reset}`);
        return { success: false, error: error.message };
    }
}

async function runAllTests() {
    const results = [];
    let passed = 0;
    let failed = 0;
    
    for (const test of tests) {
        const result = await runTest(test);
        results.push({ test: test.name, ...result });
        
        if (result.success) {
            passed++;
        } else {
            failed++;
        }
        
        console.log(''); // Línea en blanco
    }
    
    // Resumen final
    console.log(`${colors.bold}${colors.blue}📊 RESUMEN DE PRUEBAS${colors.reset}`);
    console.log(`${colors.blue}=====================${colors.reset}`);
    console.log(`${colors.green}✅ Exitosas: ${passed}${colors.reset}`);
    console.log(`${colors.red}❌ Fallidas: ${failed}${colors.reset}`);
    console.log(`📈 Total: ${results.length}`);
    
    if (failed === 0) {
        console.log(`\n${colors.green}${colors.bold}🎉 ¡INTEGRACIÓN COMPLETADA CON ÉXITO!${colors.reset}`);
        console.log(`${colors.green}✅ El frontend y backend están comunicándose correctamente${colors.reset}`);
        console.log(`${colors.green}✅ El sistema está listo para producción${colors.reset}`);
    } else {
        console.log(`\n${colors.yellow}${colors.bold}⚠️  ALGUNAS PRUEBAS FALLARON${colors.reset}`);
        console.log(`${colors.yellow}⚠️  Revisa los errores anteriores${colors.reset}`);
    }
    
    // Información adicional
    console.log(`\n${colors.blue}🔗 URLs del Sistema:${colors.reset}`);
    console.log(`   Frontend: ${FRONTEND_URL}`);
    console.log(`   Backend: ${API_BASE}`);
    console.log(`   API Health: ${API_BASE}/health`);
    console.log(`   API Docs: ${API_BASE}/docs`);
    
    return results;
}

// Ejecutar pruebas
runAllTests().catch(console.error);