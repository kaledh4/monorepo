#!/usr/bin/env node

/**
 * Build all dashboard applications
 */

const { execSync } = require('child_process');

const apps = [
    'the-shield',
    'the-coin',
    'the-map',
    'the-frontier',
    'the-strategy',
    'the-library',
    'the-commander'
];

console.log('Building all dashboard applications...\n');

let failed = [];
let succeeded = [];

apps.forEach(app => {
    try {
        console.log(`\n=== Building ${app} ===`);
        // Use npm run build:<app> to ensure the correct script (standard or vite) is used
        execSync(`npm run build:${app}`, { stdio: 'inherit' });
        succeeded.push(app);
    } catch (error) {
        console.error(`✗ Failed to build ${app}`);
        failed.push(app);
    }
});

console.log('\n=== Build Summary ===');
console.log(`✓ Succeeded: ${succeeded.length}/${apps.length}`);
if (succeeded.length > 0) {
    succeeded.forEach(app => console.log(`  ✓ ${app}`));
}

if (failed.length > 0) {
    console.log(`✗ Failed: ${failed.length}/${apps.length}`);
    failed.forEach(app => console.log(`  ✗ ${app}`));
    process.exit(1);
}

console.log('\n✓ All builds completed successfully!');

// Copy data directory to dist/data
const fs = require('fs');
const path = require('path');

const dataSrc = path.join(__dirname, '..', 'data');
const dataDest = path.join(__dirname, '..', 'dist', 'data');

if (fs.existsSync(dataSrc)) {
    console.log('\n=== Copying Data Directory ===');
    try {
        if (!fs.existsSync(dataDest)) {
            fs.mkdirSync(dataDest, { recursive: true });
        }
        
        // Recursive copy function for CommonJS
        function copyRecursiveSync(src, dest) {
            const stats = fs.statSync(src);
            if (stats.isDirectory()) {
                if (!fs.existsSync(dest)) {
                    fs.mkdirSync(dest);
                }
                fs.readdirSync(src).forEach(childItemName => {
                    copyRecursiveSync(path.join(src, childItemName), path.join(dest, childItemName));
                });
            } else {
                fs.copyFileSync(src, dest);
            }
        }

        copyRecursiveSync(dataSrc, dataDest);
        console.log(`✓ Copied data to ${dataDest}`);
    } catch (err) {
        console.error(`✗ Failed to copy data: ${err.message}`);
    }
} else {
    console.warn('⚠️ Data directory not found. Skipping copy.');
}
