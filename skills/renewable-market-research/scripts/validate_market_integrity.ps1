param(
    [Parameter(Mandatory = $true)]
    [string]$MarketJson,

    [string]$DepthDir,

    [string]$ProjectLedger,

    [string]$MetricLedger,

    [string]$CapacityReconciliation,

    [string]$OemAllocationLedger,

    [string]$ProjectCards,

    [string]$EvidenceTable,

    [string]$FactFreeze,

    [string]$CanonicalFacts,

    [string]$PhaseState,

    [string]$ArtifactManifest,

    [string[]]$ChapterInputManifest,

    [string]$ChapterInputDir,

    [string]$ChapterDraftsDir,

    [string]$AuditsDir,

    [string]$CandidatePool,

    [string]$FullReport,

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
if ($ProjectLedger) {
    $argsForPython += @("--project-ledger", $ProjectLedger)
}
if ($MetricLedger) {
    $argsForPython += @("--metric-ledger", $MetricLedger)
}
if ($CapacityReconciliation) {
    $argsForPython += @("--capacity-reconciliation", $CapacityReconciliation)
}
if ($OemAllocationLedger) {
    $argsForPython += @("--oem-allocation-ledger", $OemAllocationLedger)
}
if ($ProjectCards) {
    $argsForPython += @("--project-cards", $ProjectCards)
}
if ($EvidenceTable) {
    $argsForPython += @("--evidence-table", $EvidenceTable)
}
if ($FactFreeze) {
    $argsForPython += @("--fact-freeze", $FactFreeze)
}
if ($CanonicalFacts) {
    $argsForPython += @("--canonical-facts", $CanonicalFacts)
}
if ($PhaseState) {
    $argsForPython += @("--phase-state", $PhaseState)
}
if ($ArtifactManifest) {
    $argsForPython += @("--artifact-manifest", $ArtifactManifest)
}
if ($ChapterInputManifest) {
    foreach ($manifest in $ChapterInputManifest) {
        $argsForPython += @("--chapter-input-manifest", $manifest)
    }
}
if ($ChapterInputDir) {
    $argsForPython += @("--chapter-input-dir", $ChapterInputDir)
}
if ($ChapterDraftsDir) {
    $argsForPython += @("--chapter-drafts-dir", $ChapterDraftsDir)
}
if ($AuditsDir) {
    $argsForPython += @("--audits-dir", $AuditsDir)
}
if ($CandidatePool) {
    $argsForPython += @("--candidate-pool", $CandidatePool)
}
if ($FullReport) {
    $argsForPython += @("--full-report", $FullReport)
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
