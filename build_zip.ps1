$ErrorActionPreference = "Stop"

function Get-Version {
    $content = Get-Content "src/babylon_js/__init__.py" -Raw
    if ($content -match "'version':\s*\((\d+),\s*(\d+),\s*(\d+)\)") {
        return "$($matches[1]).$($matches[2]).$($matches[3])"
    }
    return "unknown"
}

$version = Get-Version
$zipName = "Argil_Blender_Exporter_v$version.zip"
$sourceDir = "src/babylon_js"
$tempDir = "temp_build"
$destDir = "$tempDir/babylon_js"

Write-Host "Building $zipName..."

# Cleanup previous build
if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir }
if (Test-Path $zipName) { Remove-Item -Force $zipName }

# Prepare folder structure
New-Item -ItemType Directory -Force -Path $destDir | Out-Null
Copy-Item -Recurse -Path "$sourceDir/*" -Destination $destDir

# Wait for file system to settle
Start-Sleep -Seconds 2

# Create Zip
Compress-Archive -Path "$tempDir/*" -DestinationPath $zipName -Force

# Cleanup
Remove-Item -Recurse -Force $tempDir

Write-Host "Successfully created $zipName"
