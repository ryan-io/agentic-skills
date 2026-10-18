<#
.SYNOPSIS
Links each skill under .claude\skills into the Claude Code user skills folder.

.DESCRIPTION
Creates one directory junction per skill folder (any folder holding SKILL.md)
so Claude Code, and the desktop app's Code and Cowork tabs, load skills straight
from this repo. Junctions need no admin rights and no Developer Mode. Edits in
the repo show up immediately; a newly added skill needs a re-run. Entries that
already exist in the destination are skipped, never replaced.

The Chat tab does not read this folder. Upload a ZIP of the skill folder under
Settings > Capabilities > Skills for that surface.

.PARAMETER Source
Folder holding the skill folders. Defaults to .claude\skills at the repo root.

.PARAMETER Destination
Claude Code user skills folder. Defaults to $HOME\.claude\skills.

.EXAMPLE
.\scripts\link-skills.ps1 -WhatIf
Shows what would be linked without touching the filesystem.

.EXAMPLE
.\scripts\link-skills.ps1
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$Source = (Join-Path (Split-Path $PSScriptRoot -Parent) '.claude\skills'),
    [string]$Destination = (Join-Path $HOME '.claude\skills')
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Source -PathType Container)) {
    throw "Source folder not found: $Source"
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null

$skills = Get-ChildItem $Source -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }

if (-not $skills) {
    Write-Warning "No skill folders (containing SKILL.md) under $Source"
    return
}

$linked = 0
$skipped = 0
foreach ($skill in $skills) {
    $link = Join-Path $Destination $skill.Name

    if (Test-Path $link) {
        $isReparse = (Get-Item $link -Force).Attributes -band [IO.FileAttributes]::ReparsePoint
        $kind = if ($isReparse) { 'link' } else { 'real folder' }
        Write-Host "skip   $($skill.Name)  (exists as $kind)"
        $skipped++
        continue
    }

    if ($PSCmdlet.ShouldProcess($link, "junction -> $($skill.FullName)")) {
        New-Item -ItemType Junction -Path $link -Target $skill.FullName | Out-Null
        Write-Host "linked $($skill.Name)"
        $linked++
    }
}

Write-Host ""
Write-Host "$linked linked, $skipped skipped. Destination: $Destination"
Write-Host "Restart the Claude desktop app so the Code and Cowork tabs pick up new skills."
