param(
    [Parameter(Mandatory = $true)]
    [string]$MarketJson,

    [string]$DepthDir,

    [string]$Output,

    [switch]$Strict
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir "validate_market_integrity.py"

$argsForPython = @($MarketJson)
if ($DepthDir) {
    $argsForPython += @("--depth-dir", $DepthDir)
}
if ($Output) {
    $argsForPython += @("--output", $Output)
}
if ($Strict) {
    $argsForPython += "--strict"
}

$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    & py -3 $pythonScript @argsForPython
    exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & python $pythonScript @argsForPython
    exit $LASTEXITCODE
}

throw "Python was not found. Install Python 3 or add it to PATH."
