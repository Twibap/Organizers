param([string]$FreeCADHome = 'C:\Program Files\FreeCAD 1.1')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$freecadCommand = Join-Path $FreeCADHome 'bin\FreeCADCmd.exe'
if (-not (Test-Path -LiteralPath $freecadCommand)) { throw "FreeCADCmd not found: $freecadCommand" }
$previousRoot = $env:ORGANIZER_PROJECT_ROOT
try {
    $env:ORGANIZER_PROJECT_ROOT = $projectRoot
    & $freecadCommand (Join-Path $PSScriptRoot 'headless_draft.py')
    $freecadExitCode = $LASTEXITCODE
} finally { $env:ORGANIZER_PROJECT_ROOT = $previousRoot }
if ($freecadExitCode -ne 0) { throw "Heat draft failed. Check draft-verification.json. Exit: $freecadExitCode" }
