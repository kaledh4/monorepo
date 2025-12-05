# Deploy to docs folder locally
$ErrorActionPreference = "Stop"

Write-Host "Preparing docs folder..."
if (Test-Path docs) { Remove-Item docs -Recurse -Force }
New-Item -ItemType Directory -Path docs | Out-Null

Write-Host "Copying built apps..."
Copy-Item -Path "dist/apps/*" -Destination docs -Recurse -Force

Write-Host "Copying data..."
if (Test-Path data) { Copy-Item -Path "data" -Destination docs -Recurse -Force }

Write-Host "Setting up The Commander as landing page..."
Copy-Item -Path "dist/apps/the-commander/index.html" -Destination "docs/index.html" -Force

Write-Host "Done. Ready to push."
