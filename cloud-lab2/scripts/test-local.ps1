$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
docker build --platform linux/amd64 -t cloud-lab2-api:initial .
if ($LASTEXITCODE -ne 0) { throw 'Docker build failed' }
docker rm -f cloud-lab2-api 2>$null
docker run -d --name cloud-lab2-api -p 8000:8000 cloud-lab2-api:initial
if ($LASTEXITCODE -ne 0) { throw 'Docker run failed' }
Write-Host 'Check http://localhost:8000/health and http://localhost:8000/docs'
