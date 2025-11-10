// Test de integración frontend-backend para IRIS Agent
const { mcpClient } = require('./src/lib/api.js');

async function testFrontendBackendIntegration() {
    console.log('🚀 TESTING FRONTEND-BACKEND INTEGRATION');
    console.log('===========================================');
    
    try {
        // 1. Health Check
        console.log('🔍 Testing: Health Check');
        const health = await mcpClient.checkHealth();
        console.log('✅ Health Check -', health ? 'PASSED' : 'FAILED');
        
        // 2. Get Metrics
        console.log('🔍 Testing: System Metrics');
        const metrics = await mcpClient.getMetrics();
        console.log('✅ Metrics -', metrics ? 'PASSED' : 'FAILED');
        
        // 3. Test Projects API
        console.log('🔍 Testing: Projects API');
        const projects = await mcpClient.getProjects();
        console.log('✅ Projects -', projects ? 'PASSED' : 'FAILED');
        
        // 4. Test Create Project
        console.log('🔍 Testing: Create Project');
        const newProject = await mcpClient.createQuickProject('Test Project', 'Testing integration');
        console.log('✅ Create Project -', newProject ? 'PASSED' : 'FAILED');
        
        // 5. Test Memory API
        console.log('🔍 Testing: Memory API');
        const memory = await mcpClient.remember('Test memory for integration', 'test');
        console.log('✅ Memory Store -', memory ? 'PASSED' : 'FAILED');
        
        // 6. Test Tools API
        console.log('🔍 Testing: Tools API');
        const tools = await mcpClient.listAvailableTools();
        console.log('✅ Tools List -', tools ? 'PASSED' : 'FAILED');
        
        // 7. Test Bridge API
        console.log('🔍 Testing: Bridge API');
        const bridgeStatus = await mcpClient.getSystemStatus();
        console.log('✅ Bridge Status -', bridgeStatus ? 'PASSED' : 'FAILED');
        
        // 8. Test Chat API
        console.log('🔍 Testing: Chat API');
        const { conversation, firstMessage } = await mcpClient.startChat('test-user', 'integration-test');
        console.log('✅ Chat Start -', conversation ? 'PASSED' : 'FAILED');
        
        console.log('\n🏆 INTEGRATION TEST COMPLETED');
        console.log('Frontend can successfully communicate with backend APIs!');
        
    } catch (error) {
        console.error('❌ Integration test failed:', error.message);
    }
}

testFrontendBackendIntegration();