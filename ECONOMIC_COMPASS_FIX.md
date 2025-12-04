# Economic Compass Build Issue - URGENT FIX

## Problem
The **Economic Compass** app is showing raw Jinja2 template code (`{{ }}` and `{% %}`) instead of rendered HTML because it requires a **Python build step** that is currently missing.

## Root Cause
Economic Compass uses Jinja2 templates (Python template engine) and needs to be pre-built before deployment:
- Template file: `apps/economic-compass/app/templates/index.html` (contains `{{ generated_at }}`, `{% set fng = ... %}`, etc.)
- Build script: `apps/economic-compass/build.py` (renders templates with actual data)
- Current problem: The build script copies the raw template instead of the rendered HTML

## Immediate Solution

### Option 1: Build Economic Compass Locally (Quick Fix)

```bash
cd apps/economic-compass

# Install Python dependencies
pip install -r requirements.txt

# Run the build script (requires data from unified fetcher)
python build.py

# This creates a 'public/' folder with the rendered HTML
# Copy the public folder contents to the build output
```

### Option 2: Update GitHub Actions Workflow (Permanent Fix)

The `.github/workflows/build-deploy.yml` needs to add a Python build step for economic-compass:

```yaml
- name: Build economic-compass with Python
  if: matrix.app == 'economic-compass'
  run: |
    cd apps/economic-compass
    pip install -r requirements.txt
    python build.py
    # Copy the public folder to dist
    cp -r public/* ../../dist/apps/economic-compass/
```

## Why This Happened

The unified fetcher generates data correctly (`data/economic-compass/latest.json`), but:
1. Economic Compass uses its own `data_fetcher.py` (duplicates unified fetcher)
2. The `build.py` script must be run to render templates
3. The build script (`.mjs`) only copies files, doesn't render templates

## Recommended Long-term Fix

**Convert Economic Compass to use client-side rendering** like the other apps:

1. Replace the Jinja2 template (`index.html`) with a pure HTML + JavaScript version
2. Use the unified fetcher data from `data/economic-compass/latest.json`
3. Render values dynamically with JavaScript (like hyper-analytical, crash-detector, etc.)

This would:
- ✅ Eliminate Python build dependency
- ✅ Use the unified fetcher (no duplication)
- ✅ Work consistently with other dashboards
- ✅ Deploy faster (no server-side rendering)

## Current Status

- ✅ Other 6 apps working correctly with unified fetcher
- ❌ Economic Compass showing raw templates (needs build step)
- ⚠️ Economic Compass has its own data_fetcher.py (should use unified fetcher data instead)

## Action Items

1. **SHORT TERM**: Add Python build step to GitHub Actions for economic-compass
2. **LONG TERM**: Refactor economic-compass to client-side rendering (matching other apps)
