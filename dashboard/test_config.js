
import { spawn } from 'child_process';
import http from 'http';

// Set invalid Neo4j credentials to force connection failure
const env = {
    ...process.env,
    NEO4J_URI: 'neo4j://localhost:9999', // Invalid port
    NEO4J_USER: 'neo4j',
    NEO4J_PASSWORD: 'wrong_password',
    PORT: '5002', // Use a different port for testing
    LOG_LEVEL: 'ERROR' // Reduce noise
};

console.log('🚀 Starting server with invalid Neo4j credentials...');

const server = spawn('node', ['server.js'], {
    cwd: process.cwd(),
    env
});

let serverStarted = false;

server.stdout.on('data', (data) => {
    const output = data.toString();
    // console.log(output); // Uncomment to see server logs

    if (output.includes('Dashboard available at')) {
        console.log('✅ Server started successfully despite Neo4j failure!');
        serverStarted = true;
        checkHealth();
    }
});

server.stderr.on('data', (data) => {
    // console.error(data.toString()); // Uncomment to see server errors
});

function checkHealth() {
    console.log('🏥 Checking health endpoint...');
    http.get('http://localhost:5002/api/health', (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            console.log(`Health Status: ${res.statusCode}`);
            console.log(`Response: ${data}`);

            const response = JSON.parse(data);
            if (response.status === 'healthy' && response.mode === 'offline') {
                console.log('✅ Verified: Server is running in OFFLINE MODE');
                cleanup(0);
            } else {
                console.error('❌ Unexpected response:', response);
                cleanup(1);
            }
        });
    }).on('error', (err) => {
        console.error('❌ Failed to connect to server:', err.message);
        cleanup(1);
    });
}

function cleanup(code) {
    console.log('🛑 Stopping server...');
    server.kill();
    process.exit(code);
}

// Timeout if server doesn't start
setTimeout(() => {
    if (!serverStarted) {
        console.error('❌ Timeout: Server failed to start within 10 seconds');
        cleanup(1);
    }
}, 10000);
