#
# Phyra Academic Research Plugin - Installation Script (PowerShell)
# Installs Phyra skills, agents, commands, examples, and assets
# into the user's ~/.claude/ and ~/.phyra/ directories.
#
# Usage:
#   .\scripts\install.ps1            # interactive install
#   .\scripts\install.ps1 -Update    # overwrite existing phyra files
#
param(
    [switch]$Update
)

$ErrorActionPreference = "Stop"

# --- Resolve project root ---
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$SrcDir = Join-Path $ProjectRoot "src"

$ClaudeHome = Join-Path $env:USERPROFILE ".claude"
$PhyraHome = Join-Path $env:USERPROFILE ".phyra"

# --- Verify source directory exists ---
if (-not (Test-Path $SrcDir)) {
    Write-Error "Source directory not found at $SrcDir"
    exit 1
}

# --- Check for existing phyra files ---
$existingCount = 0
foreach ($dir in @("skills", "agents", "commands")) {
    $target = Join-Path $ClaudeHome $dir
    if (Test-Path $target) {
        $existingCount += @(Get-ChildItem -Path $target -Filter "phyra-*" -ErrorAction SilentlyContinue).Count
    }
}

if ($existingCount -gt 0 -and -not $Update) {
    $confirm = Read-Host "Found $existingCount existing Phyra items in ~/.claude/. Overwrite? [y/N]"
    if ($confirm -notmatch '^[Yy]$') {
        Write-Host "Installation cancelled."
        exit 0
    }
}

# --- Create target directories ---
foreach ($p in @(
    (Join-Path $ClaudeHome "skills"),
    (Join-Path $ClaudeHome "agents"),
    (Join-Path $ClaudeHome "commands"),
    (Join-Path $PhyraHome "docs"),
    (Join-Path $PhyraHome "examples"),
    (Join-Path $PhyraHome "assets")
)) {
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
}

$installed = 0

# --- Skills (preserve directory structure) ---
Get-ChildItem -Path (Join-Path $SrcDir "skills") -Directory -Filter "phyra-*" | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $ClaudeHome "skills" $_.Name) -Recurse -Force
    $installed++
    Write-Host "  skill: $($_.Name)/"
}

# --- Agents ---
Get-ChildItem -Path (Join-Path $SrcDir "agents") -Filter "phyra-*.md" | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $ClaudeHome "agents" $_.Name) -Force
    $installed++
    Write-Host "  agent: $($_.Name)"
}

# --- Commands ---
Get-ChildItem -Path (Join-Path $SrcDir "commands") -Filter "phyra-*.md" | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $ClaudeHome "commands" $_.Name) -Force
    $installed++
    Write-Host "  command: $($_.Name)"
}

# --- Support docs ---
Get-ChildItem -Path (Join-Path $SrcDir "support") -Filter "*.md" | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $PhyraHome "docs" $_.Name) -Force
    $installed++
    Write-Host "  doc: $($_.Name)"
}

# --- Examples ---
Get-ChildItem -Path (Join-Path $SrcDir "examples") -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $PhyraHome "examples" $_.Name) -Force
    $installed++
    Write-Host "  example: $($_.Name)"
}

# --- Assets ---
Get-ChildItem -Path (Join-Path $SrcDir "assets") -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $PhyraHome "assets" $_.Name) -Force
    $installed++
    Write-Host "  asset: $($_.Name)"
}

Write-Host ""
Write-Host "Installed $installed items."

# --- Agent Teams config ---
$SettingsFile = Join-Path $ClaudeHome "settings.json"
Write-Host ""
$enableTeams = Read-Host "Enable Agent Teams in ~/.claude/settings.json? [y/N]"
if ($enableTeams -match '^[Yy]$') {
    if (Test-Path $SettingsFile) {
        $settings = Get-Content $SettingsFile -Raw | ConvertFrom-Json
        if ($settings.PSObject.Properties.Name -contains "env" -and
            $settings.env.PSObject.Properties.Name -contains "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS") {
            Write-Host "Agent Teams config already present in settings.json."
        } else {
            if (-not ($settings.PSObject.Properties.Name -contains "env")) {
                $settings | Add-Member -NotePropertyName "env" -NotePropertyValue ([PSCustomObject]@{})
            }
            $settings.env | Add-Member -NotePropertyName "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" -NotePropertyValue "1" -Force
            $settings | ConvertTo-Json -Depth 10 | Set-Content $SettingsFile -Encoding UTF8
            Write-Host "Added Agent Teams config to existing settings.json."
        }
    } else {
        @{ env = @{ CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1" } } | ConvertTo-Json -Depth 10 | Set-Content $SettingsFile -Encoding UTF8
        Write-Host "Created settings.json with Agent Teams config."
    }
}

Write-Host ""
Write-Host "Phyra installation complete."
