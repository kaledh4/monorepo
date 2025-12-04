#!/usr/bin/env node

/**
 * Simple build script for static dashboard apps
 * Copies app files to dist directory and generates PWA assets
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { generateServiceWorker, getManifestForDashboard } from '../libs/shared-pwa/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const appName = process.argv[2];

if (!appName) {
    console.error('Usage: node build-app.mjs <app-name>');
    process.exit(1);
}

const sourceDir = path.join(__dirname, '..', 'apps', appName);
const distDir = path.join(__dirname, '..', 'dist', 'apps', appName);

// Check if source directory exists
if (!fs.existsSync(sourceDir)) {
    console.error(`Error: App directory not found: ${sourceDir}`);
    process.exit(1);
}

// Create dist directory
if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
}

// Copy files recursively
function copyRecursive(src, dest) {
    const stats = fs.statSync(src);

    if (stats.isDirectory()) {
        // Skip certain directories
        const dirName = path.basename(src);
        if (dirName === 'node_modules' || dirName === '.git' || dirName === '__pycache__' || dirName === '.github' || dirName === 'briefs') {
            return;
        }

        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }

        const files = fs.readdirSync(src);
        files.forEach(file => {
            copyRecursive(path.join(src, file), path.join(dest, file));
        });
    } else {
        // Skip certain file types
        const ext = path.extname(src);
        const basename = path.basename(src);
        // We skip manifest.json and service-worker.js because we generate them, 
        // unless we want to preserve custom ones. But the goal is to use shared logic.
        // Let's skip them for now and overwrite later.
        if (ext === '.py' || ext === '.txt' || ext === '.md' || ext === '.ps1' || basename === 'project.json' || basename.endsWith('.backup') || basename === 'package.json' || basename === 'package-lock.json') {
            return;
        }

        fs.copyFileSync(src, dest);
        console.log(`Copied: ${path.relative(sourceDir, src)}`);
    }
}

console.log(`Building ${appName}...`);
console.log(`Source: ${sourceDir}`);
console.log(`Destination: ${distDir}`);

// Special handling for different app structures
// Special handling for different app structures
if (appName === 'economic-compass' || appName === 'the-map') {
    // economic-compass/the-map: files in app/static and app/templates
    const staticDir = path.join(sourceDir, 'app', 'static');
    const templatesDir = path.join(sourceDir, 'app', 'templates');

    if (fs.existsSync(staticDir)) {
        console.log('Copying static files...');
        copyRecursive(staticDir, distDir);
    }

    if (fs.existsSync(templatesDir)) {
        console.log('Copying template files...');
        const files = fs.readdirSync(templatesDir);
        files.forEach(file => {
            if (file.endsWith('.html') && !file.endsWith('.backup')) {
                const src = path.join(templatesDir, file);
                const dest = path.join(distDir, file);
                fs.copyFileSync(src, dest);
                console.log(`Copied: ${file}`);
            }
        });
    }
} else if (appName === 'ai-race' || appName === 'the-frontier') {
    // ai-race/the-frontier: files in AI_RACE_CLEAN-main subdirectory
    const subDir = path.join(sourceDir, 'AI_RACE_CLEAN-main');
    if (fs.existsSync(subDir)) {
        console.log('Copying from AI_RACE_CLEAN-main...');
        copyRecursive(subDir, distDir);
    } else {
        copyRecursive(sourceDir, distDir);
    }
} else {
    // Other apps: copy from root
    copyRecursive(sourceDir, distDir);
}

// Generate PWA Assets
console.log('Generating PWA assets...');

try {
    // 1. Generate Manifest
    const manifest = getManifestForDashboard(appName);
    // The manifest now has proper absolute paths for id, scope, and start_url
    // This ensures each app is uniquely identified by the browser

    fs.writeFileSync(path.join(distDir, 'manifest.json'), JSON.stringify(manifest, null, 2));
    console.log('✓ Generated manifest.json');

    // 2. Generate Service Worker
    // We need to know which assets to cache. 
    // A simple heuristic: list all files in distDir recursively.

    function getAllFiles(dirPath, arrayOfFiles) {
        const files = fs.readdirSync(dirPath);
        arrayOfFiles = arrayOfFiles || [];

        files.forEach(function (file) {
            if (fs.statSync(dirPath + "/" + file).isDirectory()) {
                arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles);
            } else {
                arrayOfFiles.push(path.join(dirPath, file));
            }
        });

        return arrayOfFiles;
    }

    const allFiles = getAllFiles(distDir);
    const assetsToCache = allFiles
        .map(f => path.relative(distDir, f))
        .map(f => './' + f.replace(/\\/g, '/')); // Ensure forward slashes and relative path

    // Filter out service-worker.js itself to avoid recursion issues (though usually fine)
    // and maybe map files.

    const swContent = generateServiceWorker({
        appName,
        version: Date.now().toString(), // Use timestamp for unique versioning
        assetsToCache
    });

    fs.writeFileSync(path.join(distDir, 'service-worker.js'), swContent);
    console.log('✓ Generated service-worker.js');

} catch (error) {
    console.error('Error generating PWA assets:', error);
    // Don't fail the build, just warn? Or fail?
    // If PWA is critical, we should probably fail or at least log heavily.
    console.error('Continuing build without PWA updates...');
}

console.log(`✓ Build complete for ${appName}`);
