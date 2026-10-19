<#
.SYNOPSIS
Links this repo's harness (skills, agents, rules, CLAUDE.md) into the Claude Code user folder.

.DESCRIPTION
Makes the harness apply to every Claude Code session on this machine, with the repo
as the single source of truth. Junctions need no admin rights and no Developer Mode.

  skills   one junction per skill folder (any folder holding SKILL.md)
           -> $HOME\.claude\skills\<name>
  agents   one junction for the whole folder -> $HOME\.claude\agents
  rules    one junction for the whole folder -> $HOME\.claude\rules
  CLAUDE   adds "@<repo>/CLAUDE.md" to $HOME\.claude\CLAUDE.md (created if missing)

Existing entries are never replaced. A real folder at the agents or rules destination
is replaced only when it is empty; otherwise it is reported and skipped.

Known limits (code.claude.com/docs/en/memory, read 2026-10-18):
  - Cowork tab sessions skip a linked rules folder and a CLAUDE.md import that point
    outside the working directory. Code tab and the CLI load them.
  - The Chat tab reads none of this; upload a skill ZIP under Settings > Capabilities.
  - A newly added skill needs a re-run. Agents and rules pick up new files immediately.

.PARAMETER RepoRoot
Harness repo root. Defaults to the parent of this script's folder.

.PARAMETER ClaudeHome
Claude Code user folder. Defaults to $HOME\.claude.

.PARAMETER NoClaudeMd
Skip the CLAUDE.md import step.

.EXAMPLE
.\scripts\link-harness.ps1 -WhatIf

.EXAMPLE
.\scripts\link-harness.ps1
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$RepoRoot = (Split-Path $PSScriptRoot -Parent),
    [string]$ClaudeHome = (Join-Path $HOME '.claude'),
    [switch]$NoClaudeMd
)

$ErrorActionPreference = 'Stop'
$harness = Join-Path $RepoRoot '.claude'
if (-not (Test-Path $harness -PathType Container)) {
    throw "Harness folder not found: $harness"
}
New-Item -ItemType Directory -Force -Path $ClaudeHome | Out-Null

function Describe-Existing([string]$Path) {
    $item = Get-Item $Path -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { return "link -> $($item.Target)" }
    if ($item.PSIsContainer) { return 'real folder' }
    return 'file'
}

function New-Junction([string]$Link, [string]$Target, [string]$Label) {
    if ($PSCmdlet.ShouldProcess($Link, "junction -> $Target")) {
        New-Item -ItemType Junction -Path $Link -Target $Target | Out-Null
        Write-Host "linked $Label"
        return $true
    }
    return $false
}

$linked = 0
$skipped = 0

# --- skills: one junction per skill folder ---------------------------------
$skillsSrc = Join-Path $harness 'skills'
$skillsDst = Join-Path $ClaudeHome 'skills'
New-Item -ItemType Directory -Force -Path $skillsDst | Out-Null
$skills = Get-ChildItem $skillsSrc -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }
if (-not $skills) { Write-Warning "No skill folders (containing SKILL.md) under $skillsSrc" }
foreach ($skill in $skills) {
    $link = Join-Path $skillsDst $skill.Name
    if (Test-Path $link) {
        Write-Host "skip   skills\$($skill.Name)  (exists as $(Describe-Existing $link))"
        $skipped++
        continue
    }
    if (New-Junction $link $skill.FullName "skills\$($skill.Name)") { $linked++ }
}

# --- agents, rules: one junction for the whole folder ------------------------
foreach ($name in 'agents', 'rules') {
    $src = Join-Path $harness $name
    $dst = Join-Path $ClaudeHome $name
    if (-not (Test-Path $src -PathType Container)) {
        Write-Warning "No $name folder under $harness; skipped"
        continue
    }
    if (Test-Path $dst) {
        $item = Get-Item $dst -Force
        $isLink = $item.Attributes -band [IO.FileAttributes]::ReparsePoint
        $isEmptyDir = (-not $isLink) -and $item.PSIsContainer -and
            -not (Get-ChildItem $dst -Force | Select-Object -First 1)
        if ($isEmptyDir) {
            if ($PSCmdlet.ShouldProcess($dst, 'remove empty folder')) { Remove-Item $dst }
        }
        else {
            Write-Host "skip   $name  (exists as $(Describe-Existing $dst))"
            $skipped++
            continue
        }
    }
    if (New-Junction $dst $src $name) { $linked++ }
}

# --- CLAUDE.md: import the repo's entry point ---------------------------------
if (-not $NoClaudeMd) {
    $repoClaudeMd = Join-Path $RepoRoot 'CLAUDE.md'
    if (-not (Test-Path $repoClaudeMd -PathType Leaf)) {
        Write-Warning "No CLAUDE.md at $RepoRoot; import skipped"
    }
    else {
        $userClaudeMd = Join-Path $ClaudeHome 'CLAUDE.md'
        $importLine = '@' + ($repoClaudeMd -replace '\\', '/')
        $present = (Test-Path $userClaudeMd) -and
            (Select-String -Path $userClaudeMd -SimpleMatch -Pattern $importLine -Quiet)
        if ($present) {
            Write-Host "skip   CLAUDE.md  (import already present)"
            $skipped++
        }
        elseif ($PSCmdlet.ShouldProcess($userClaudeMd, "append $importLine")) {
            Add-Content -Path $userClaudeMd -Value $importLine -Encoding utf8
            Write-Host "linked CLAUDE.md  ($importLine)"
            $linked++
        }
    }
}

Write-Host ""
Write-Host "$linked linked, $skipped skipped. Claude home: $ClaudeHome"
Write-Host "Restart the Claude desktop app so the Code and Cowork tabs pick up the changes."
