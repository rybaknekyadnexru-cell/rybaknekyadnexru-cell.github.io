# Build the site and publish it: .\publish.ps1 "what changed"
param([string]$Message = "chore: update site")
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python build.py
git add -A
git commit -m $Message
git push
