param(
    [Parameter(Mandatory=$true)][string]$RomPath,
    [Parameter(Mandatory=$true)][string]$OutputDir
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot | Split-Path -Parent
$ExpectedHash = "9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9"

$Python = if ($env:ROLO_PYTHON) { $env:ROLO_PYTHON } else { (Get-Command python -ErrorAction Stop).Source }

function Run-Python {
    param([string]$Script, [string[]]$Arguments)

    $Path = Join-Path $Root "tools\$Script"

    if (!(Test-Path $Path)) {
        throw "Required extraction tool missing: $Script"
    }

    Write-Host "`nEXTRACT: $Script" -ForegroundColor Cyan

    & $Python $Path @Arguments

    if ($LASTEXITCODE -ne 0) {
        throw "Extraction failed: $Script"
    }
}

$RomPath = (Resolve-Path $RomPath).Path
$Hash = (Get-FileHash $RomPath -Algorithm SHA256).Hash

if ($Hash -ne $ExpectedHash) {
    throw "Unsupported ROM revision. SHA256: $Hash"
}

Write-Host "Original Rolo ROM verified." -ForegroundColor Green

# Existing extraction utilities expect local/rolo.md.
$Local = Join-Path $Root "local"
New-Item -ItemType Directory -Force $Local, $OutputDir | Out-Null
$DestinationRom = Join-Path $Local "rolo.md"

$SourceFull = [IO.Path]::GetFullPath($RomPath)
$DestinationFull = [IO.Path]::GetFullPath($DestinationRom)

if (![string]::Equals(
    $SourceFull,
    $DestinationFull,
    [StringComparison]::OrdinalIgnoreCase
)) {
    Copy-Item -LiteralPath $RomPath `
        -Destination $DestinationRom -Force
}

# 1. Extract catalogue and artwork.
Run-Python "dump_images.py" @(
    "$Local\rolo.md",
    "--out", "$Root\assets\extracted"
)

# Build the complete ROM asset catalogue first.
Run-Python "inventory_assets.py" @(
    "$Local\rolo.md",
    "--out", "$Root\assets\extracted\catalog"
)

Run-Python "inventory_first_level.py" @(
    "$Local\rolo.md",
    "--project", $Root
)

# Build the animation catalogue.
Run-Python "inventory_animations.py" @(
    "$Local\rolo.md",
    "--out", "$Root\assets\extracted\catalog\animations"
)

# Verify both catalogues before continuing.
foreach ($Manifest in @(
    "$Root\assets\extracted\catalog\manifest.json",
    "$Root\assets\extracted\catalog\animations\manifest.json"
)) {
    if (!(Test-Path -LiteralPath $Manifest)) {
        throw "Catalogue generation failed: $Manifest"
    }
}
# 2. Extract connected level maps and graphics banks.
Run-Python "bulk_extract_levels.py" @(
    "--project", $Root,
    "--rom", "$Local\rolo.md"
)

# 3. Regenerate native level data and object resources.
Run-Python "rebuild_connected_level_assets.py" @()

# 4. Generate standalone player assets.
Run-Python "export_player.py" @(
    "$Local\rolo.md",
    "--project", $Root
)

# 5. Generate world map artwork.
Run-Python "export_world_cursor.py" @()
Run-Python "export_world_bunny.py" @()

# 6. Generate enemy artwork.
Run-Python "export_first_enemy.py" @(
    "$Local\rolo.md",
    "--project", $Root
)
Run-Python "export_enemy_preview_assets.py" @()

# 7. Generate entrance animations and graphics.
$EntranceHeader = "$Root\src\core\entrance_data.hpp"

$EntranceCode = @"
import pathlib, sys
sys.path.insert(0, r'$($Root.Replace("'", "\'"))\tools')
import export_entrance
rom = pathlib.Path(r'$($Local.Replace("'", "\'"))\rolo.md').read_bytes()
export_entrance.export(rom, pathlib.Path(r'$($EntranceHeader.Replace("'", "\'"))'))
"@

Write-Host "`nEXTRACT: Entrance animation data" -ForegroundColor Cyan
& $Python -c $EntranceCode

if ($LASTEXITCODE -ne 0) {
    throw "Entrance animation extraction failed."
}

Run-Python "export_preview.py" @(
    "$Local\rolo.md",
    "--header", $EntranceHeader,
    "--out", "$OutputDir\entrance-assets.rla"
)

# 8. Regenerate ending and forest resources.
Run-Python "export_ending_assets.py" @()
Run-Python "export_forest_log.py" @()

# 9. Verify all CMake-required asset packs.
$Required = @(
    "world-cursor-assets.rla",
    "world-bunny-assets.rla",
    "entrance-assets.rla",
    "player-assets.rla",
    "level1-player-assets.rla",
    "first-enemy-assets.rla",
    "level1-object-assets.rla"
)

foreach ($Asset in $Required) {
    $Path = Join-Path $OutputDir $Asset

    if (!(Test-Path $Path)) {
        throw "Missing extracted asset: $Asset"
    }

    if ((Get-Item $Path).Length -le 12) {
        throw "Invalid or empty asset: $Asset"
    }

    $Bytes = [IO.File]::ReadAllBytes($Path)
    $Magic = [Text.Encoding]::ASCII.GetString($Bytes, 0, 8)

    if ($Magic -ne ("RLOAS01" + [char]0)) {
        throw "Incorrect asset format: $Asset"
    }

    Write-Host "OK: $Asset" -ForegroundColor Green
}

Write-Host "`nROM extraction completed." -ForegroundColor Green


