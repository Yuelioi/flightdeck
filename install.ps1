<#
.SYNOPSIS
    Install all flightdeck skills into your AI tool's skills directory.

.DESCRIPTION
    Detects installed AI tools and copies every skills/* subdir to the
    appropriate target. Installs preflight + launch + walkaround.

    Creating a deck is not part of install — run /flightdeck:launch in a
    session; it copies the scaffold shipped inside the launch skill.

.PARAMETER Tool
    Which AI tool to install for. Default: auto-detect.
    Supported (active):  claude
    Stub (PRs welcome):  codex, cursor, gemini

.PARAMETER Force
    Overwrite an existing install without prompting.

.EXAMPLE
    .\install.ps1
    Auto-detects AI tool and installs the skills.

.EXAMPLE
    .\install.ps1 -Tool claude -Force
    Installs the Claude adapter, overwriting any existing install.
#>

[CmdletBinding()]
param(
    [ValidateSet('auto', 'claude', 'codex', 'cursor', 'gemini')]
    [string]$Tool = 'auto',

    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillsSource = Join-Path $repoRoot 'skills'

if (-not (Test-Path $skillsSource)) {
    Write-Error "Skills source not found: $skillsSource"
    exit 1
}

function Detect-Tool {
    $claudeDir = Join-Path $env:USERPROFILE '.claude'
    if (Test-Path $claudeDir) { return 'claude' }

    $codexDir = Join-Path $env:USERPROFILE '.agents'
    if (Test-Path $codexDir) { return 'codex' }

    return $null
}

function Install-Claude {
    $skillsDir = Join-Path $env:USERPROFILE '.claude\skills'
    if (-not (Test-Path $skillsDir)) {
        New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
    }

    $installed = @()
    Get-ChildItem -Directory $skillsSource | ForEach-Object {
        $skillName = $_.Name
        $target = Join-Path $skillsDir $skillName

        if ((Test-Path $target) -and -not $Force) {
            Write-Host "Target already exists: $target"
            $answer = Read-Host "Overwrite? [y/N]"
            if ($answer -ne 'y' -and $answer -ne 'Y') {
                Write-Host "Skipped: $skillName"
                return
            }
        }
        if (Test-Path $target) {
            Remove-Item -Recurse -Force $target
        }
        Copy-Item -Recurse $_.FullName $target
        $installed += $skillName
    }

    if ($installed.Count -gt 0) {
        Write-Host ("Installed skills: " + ($installed -join ', ')) -ForegroundColor Green
        Write-Host "Target dir: $skillsDir"
        Write-Host "Verify: in a Claude Code session, run /flightdeck:preflight or check the skill list."
    }
}

function Install-Stub {
    param([string]$ToolName)
    $adapterReadme = Join-Path $repoRoot "adapters\$ToolName\README.md"
    Write-Host ""
    Write-Host "Adapter '$ToolName' is a stub (no active install logic yet)." -ForegroundColor Yellow
    Write-Host "See: $adapterReadme"
    Write-Host "PRs welcome."
    Write-Host ""
}

# --- main ---

if ($Tool -eq 'auto') {
    $detected = Detect-Tool
    if ($null -eq $detected) {
        Write-Host "Could not auto-detect an AI tool. Specify with -Tool <claude|codex|cursor|gemini>."
        exit 1
    }
    $Tool = $detected
    Write-Host "Auto-detected: $Tool"
}

switch ($Tool) {
    'claude' { Install-Claude }
    'codex'  { Install-Stub -ToolName 'codex' }
    'cursor' { Install-Stub -ToolName 'cursor' }
    'gemini' { Install-Stub -ToolName 'gemini' }
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green
