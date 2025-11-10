#!/usr/bin/env node

/**
 * Script de testing para verificar la integración frontend-backend
 * IRIS Code - Testing de conectividad y funcionalidad
 */

const axios = require('axios');
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

class IRISCodeTester {
  constructor(baseUrl = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
    this.results = {
      total: 0,
      passed: 0,
      failed: 0,
      details: []
    };
  }

  async testEndpoint(name, method, url, options = {}) {
    this.results.total++;
    const fullUrl = url.startsWith('http') ? url : `${this.baseUrl}${url}`;
    
    try {
      const response = await axios({
        method,
        url: fullUrl,
        timeout: 10000,
        ...options
      });
      
      this.results.passed++;
      this.results.details.push({
        name,
        status: 'PASS',
        statusCode: response.status,
        response: this.sanitizeResponse(response.data)
      });
      
      console.log(`${colors.green}✓${colors.reset} ${name} - Status: ${response.status}`);
      return { success: true, data: response.data, status: response.status };
      
    } catch (error) {
      this.results.failed++;
      const statusCode = error.response?.status || 'NETWORK_ERROR';
      const message = error.message;
      
      this.results.details.push({
        name,
        status: 'FAIL',
        statusCode,
        error: message,
        response: error.response?.data
      });
      
      console.log(`${colors.red}✗${colors.reset} ${name} - Error: ${statusCode} ${message}`);
      return { success: false, error: message, status: statusCode };
    }
  }

  sanitizeResponse(data) {
    if (typeof data === 'string') return data.substring(0, 200);
    if (data && typeof data === 'object') {
      const sanitized = { ...data };
      if (sanitized.content && sanitized.content.length > 200) {
        sanitized.content = sanitized.content.substring(0, 200) + '...';
      }
      return sanitized;
    }
    return data;
  }

  async runAllTests() {
    console.log(`${colors.bright}🧪 IRIS Code - Testing Frontend Integration${colors.reset}\n`);
    console.log(`Testing backend at: ${colors.cyan}${this.baseUrl}${colors.reset}\n`);

    // Health Check
    await this.testEndpoint(
      'Health Check',
      'GET',
      '/health'
    );

    // Metrics
    await this.testEndpoint(
      'Metrics Endpoint',
      'GET',
      '/metrics'
    );

    // Projects API
    await this.testEndpoint(
      'List Projects',
      'GET',
      '/api/v1/projects'
    );

    await this.testEndpoint(
      'Create Project',
      'POST',
      '/api/v1/projects',
      {
        data: {
          name: 'Test Project',
          description: 'Proyecto de prueba para testing'
        }
      }
    );

    // Chat API
    await this.testEndpoint(
      'Chat Endpoint',
      'POST',
      '/api/v1/chat',
      {
        data: {
          message: 'Hola, este es un mensaje de prueba',
          context: 'testing'
        }
      }
    );

    await this.testEndpoint(
      'Chat Stream Endpoint',
      'POST',
      '/api/v1/chat/stream',
      {
        data: {
          message: 'Mensaje para testing de streaming',
          stream: true
        }
      }
    );

    // Templates
    await this.testEndpoint(
      'Templates Endpoint',
      'GET',
      '/api/v1/templates'
    );

    // CORS Test
    await this.testEndpoint(
      'CORS Configuration',
      'OPTIONS',
      '/api/v1/projects',
      {
        headers: {
          'Origin': 'http://localhost:3000',
          'Access-Control-Request-Method': 'GET'
        }
      }
    );

    this.printSummary();
    return this.results;
  }

  printSummary() {
    console.log(`\n${colors.bright}📊 Test Summary${colors.reset}`);
    console.log(`Total Tests: ${this.results.total}`);
    console.log(`${colors.green}Passed: ${this.results.passed}${colors.reset}`);
    console.log(`${colors.red}Failed: ${this.results.failed}${colors.reset}`);
    
    const successRate = (this.results.passed / this.results.total * 100).toFixed(1);
    console.log(`Success Rate: ${successRate}%`);

    if (this.results.failed > 0) {
      console.log(`\n${colors.red}❌ Failed Tests:${colors.reset}`);
      this.results.details
        .filter(test => test.status === 'FAIL')
        .forEach(test => {
          console.log(`  - ${test.name}: ${test.statusCode} ${test.error}`);
        });
    }

    if (this.results.passed === this.results.total) {
      console.log(`\n${colors.green}🎉 All tests passed! Frontend integration is ready.${colors.reset}`);
    } else {
      console.log(`\n${colors.yellow}⚠️  Some tests failed. Check the configuration and backend status.${colors.reset}`);
    }
  }

  // Frontend-specific tests
  async testFrontendIntegration() {
    console.log(`\n${colors.bright}🔗 Testing Frontend Integration${colors.reset}`);

    // Test if frontend can reach backend
    const frontendTests = [
      {
        name: 'Frontend → Backend Communication',
        test: () => this.testEndpoint('Basic Connectivity', 'GET', '/health')
      },
      {
        name: 'API Routes Mapping',
        test: () => this.testEndpoint('Projects API', 'GET', '/api/v1/projects')
      },
      {
        name: 'CORS Headers',
        test: async () => {
          try {
            const response = await axios.get(`${this.baseUrl}/api/v1/projects`, {
              headers: { 'Origin': 'http://localhost:3000' }
            });
            const hasCorsHeaders = response.headers['access-control-allow-origin'] || 
                                   response.headers['Access-Control-Allow-Origin'];
            
            if (hasCorsHeaders) {
              console.log(`${colors.green}✓${colors.reset} CORS Headers - Properly configured`);
              return { success: true };
            } else {
              console.log(`${colors.yellow}!${colors.reset} CORS Headers - May need configuration`);
              return { success: false, warning: 'CORS headers not detected' };
            }
          } catch (error) {
            return { success: false, error: error.message };
          }
        }
      }
    ];

    for (const test of frontendTests) {
      await test.test();
    }
  }
}

// CLI Interface
async function main() {
  const args = process.argv.slice(2);
  const baseUrl = args.find(arg => arg.startsWith('--url='))?.split('=')[1] || 'http://localhost:8001';
  
  const tester = new IRISCodeTester(baseUrl);
  
  try {
    await tester.runAllTests();
    await tester.testFrontendIntegration();
    
    // Exit with appropriate code
    process.exit(tester.results.failed > 0 ? 1 : 0);
    
  } catch (error) {
    console.error(`${colors.red}Error running tests:${colors.reset}`, error.message);
    process.exit(1);
  }
}

// If running directly
if (require.main === module) {
  main();
}

module.exports = IRISCodeTester;