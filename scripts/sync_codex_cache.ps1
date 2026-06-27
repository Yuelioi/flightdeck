param(
    [string]$RepoRoot,
    [string]$CodexHome,
    [string]$MarketplaceName = "flightdeck-marketplace",
    [string]$PluginName,
    [string]$Version,
    [switch]$DryRun,
    [switch]$SkipStamp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-FullPath([string]$Path) {
    return [System.IO.Path]::GetFullPath($Path)
}

function Test-IsUnderPath([string]$Child, [string]$Parent) {
    $childFull = Resolve-FullPath $Child
    $parentFull = (Resolve-FullPath $Parent).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    return $childFull.StartsWith($parentFull + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
}

if (-not $RepoRoot) {
    $RepoRoot = Resolve-FullPath (Join-Path $PSScriptRoot "..")
} else {
    $RepoRoot = Resolve-FullPath $RepoRoot
}

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    throw "Repo root does not exist: $RepoRoot"
}

if (-not $CodexHome) {
    if ($env:CODEX_HOME) {
        $CodexHome = $env:CODEX_HOME
    } else {
        $CodexHome = Join-Path $HOME ".codex"
    }
}
$CodexHome = Resolve-FullPath $CodexHome

$manifestPath = Join-Path $RepoRoot ".codex-plugin\plugin.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Missing Codex plugin manifest: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if (-not $PluginName) {
    $PluginName = [string]$manifest.name
}
if (-not $PluginName) {
    throw "Plugin name was not provided and .codex-plugin/plugin.json has no name."
}

$cacheRoot = Join-Path $CodexHome "plugins\cache"
$pluginCacheRoot = Join-Path $cacheRoot (Join-Path $MarketplaceName $PluginName)

if (-not (Test-Path -LiteralPath $pluginCacheRoot -PathType Container)) {
    throw "Codex cache root does not exist for $PluginName@$MarketplaceName`: $pluginCacheRoot. Install the plugin first."
}

if (-not $Version) {
    $versionDirs = @(Get-ChildItem -LiteralPath $pluginCacheRoot -Directory | Sort-Object LastWriteTime -Descending)
    if ($versionDirs.Count -eq 0) {
        throw "No installed version directories found under $pluginCacheRoot."
    }
    if ($versionDirs.Count -gt 1) {
        Write-Warning "Multiple cache versions found; using most recently modified: $($versionDirs[0].Name)"
    }
    $Version = $versionDirs[0].Name
}

$destination = Resolve-FullPath (Join-Path $pluginCacheRoot $Version)
if (-not (Test-Path -LiteralPath $destination -PathType Container)) {
    throw "Destination cache version does not exist: $destination"
}
if (-not (Test-IsUnderPath $destination $cacheRoot)) {
    throw "Refusing to mirror outside Codex plugin cache: $destination"
}

$stampScript = Join-Path $RepoRoot "scripts\build_stamp.py"
if (-not $SkipStamp -and (Test-Path -LiteralPath $stampScript -PathType Leaf)) {
    if ($DryRun) {
        Write-Host "DRY RUN: would write build stamp with: uv run `"$stampScript`" --write"
    } else {
        & uv run $stampScript --write
        if ($LASTEXITCODE -ne 0) {
            throw "build_stamp.py --write failed with exit code $LASTEXITCODE"
        }
    }
}

$robocopyArgs = @(
    $RepoRoot,
    $destination,
    "/MIR",
    "/XD", ".git", "tmp", ".vscode", ".superpowers", "references", "__pycache__", ".pytest_cache",
    "/XF", ".in_use", "*.pyc", "*.pyo"
)

Write-Host "Source:      $RepoRoot"
Write-Host "Destination: $destination"
Write-Host "Plugin:      $PluginName@$MarketplaceName ($Version)"

if ($DryRun) {
    Write-Host "DRY RUN: robocopy $($robocopyArgs -join ' ') /L"
    & robocopy @robocopyArgs /L
} else {
    & robocopy @robocopyArgs
}

$code = $LASTEXITCODE
if ($code -ge 8) {
    throw "robocopy failed with exit code $code"
}

$cacheManifestPath = Join-Path $destination ".codex-plugin\plugin.json"
if (Test-Path -LiteralPath $cacheManifestPath -PathType Leaf) {
    $cacheManifest = Get-Content -LiteralPath $cacheManifestPath -Raw | ConvertFrom-Json
    Write-Host "Cache manifest version: $($cacheManifest.version)"
}

if ($DryRun) {
    Write-Host "Dry run complete. Codex cache was not modified."
} else {
    Write-Host "Codex cache sync complete. Start a new Codex thread to load the updated plugin."
}
