param(
    [switch]$Verify,
    [string]$FreeCADHome = 'C:\Program Files\FreeCAD 1.1'
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$freecadCommand = Join-Path $FreeCADHome 'bin\FreeCADCmd.exe'
if (-not (Test-Path -LiteralPath $freecadCommand)) {
    throw "FreeCADCmd was not found at $freecadCommand. Supply -FreeCADHome."
}
$previousRoot = $env:ORGANIZER_PROJECT_ROOT
$previousVerify = $env:ORGANIZER_VERIFY
try {
    $env:ORGANIZER_PROJECT_ROOT = $projectRoot
    $env:ORGANIZER_VERIFY = if ($Verify) { '1' } else { '0' }
    & $freecadCommand (Join-Path $PSScriptRoot 'headless_demo.py')
    $freecadExitCode = $LASTEXITCODE
} finally {
    $env:ORGANIZER_PROJECT_ROOT = $previousRoot
    $env:ORGANIZER_VERIFY = $previousVerify
}
if ($freecadExitCode -ne 0) {
    throw "FreeCAD demo failed with exit code $freecadExitCode. Check verification.json."
}
