$ErrorActionPreference = 'Stop'
$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $AppRoot 'runtime\python\python.exe'
$Template = Join-Path $AppRoot 'ExtractorTemplate'
$Game = Join-Path $AppRoot 'RoloGame.exe'
$AppDataRoot = Join-Path $env:LOCALAPPDATA 'RoloToTheRescue'
$DataRoot = Join-Path $AppDataRoot 'resources-v1'
$ExpectedRomSha256 = '9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'
$ExpectedManifestSha256 = 'c1d41a485c8e3f383d7a3745b409d12bb66450865648c8453c635aa87d3ce95e'
$RequiredAssets = @(
    'entrance-assets.rla', 'player-assets.rla', 'level1-player-assets.rla',
    'first-enemy-assets.rla', 'level1-object-assets.rla',
    'world-cursor-assets.rla', 'world-bunny-assets.rla'
)

if (!(Test-Path $Game) -or !(Test-Path $Python)) {
    throw 'Rolo is missing a required program. Re-extract the downloaded package and try again.'
}

function Test-ReadyPack([string]$Root) {
    $manifest = Join-Path $Root 'manifest.json'
    if (!(Test-Path $manifest)) { return $false }
    if ((Get-FileHash $manifest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ExpectedManifestSha256) { return $false }
    foreach ($asset in $RequiredAssets) {
        $file = Join-Path $Root $asset
        if (!(Test-Path $file) -or (Get-Item $file).Length -le 12) { return $false }
    }
    & $Python (Join-Path $AppRoot 'verify_pack.py') $Root | Out-Null
    return $LASTEXITCODE -eq 0
}

if (!(Test-ReadyPack $DataRoot)) {
    Add-Type -AssemblyName System.Windows.Forms
    $picker = New-Object System.Windows.Forms.OpenFileDialog
    $picker.Title = 'Choose your Rolo to the Rescue ROM'
    $picker.Filter = 'Rolo ROM (*.md;*.sfc;*.smc;*.bin)|*.md;*.sfc;*.smc;*.bin|All files (*.*)|*.*'
    $picker.CheckFileExists = $true
    $picker.Multiselect = $false
    if ($picker.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { exit 0 }
    $rom = (Resolve-Path -LiteralPath $picker.FileName).Path
    $romInfo = Get-Item -LiteralPath $rom
    if ($romInfo.Length -ne 524288 -or (Get-FileHash -LiteralPath $rom -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ExpectedRomSha256) {
        [System.Windows.Forms.MessageBox]::Show('That file is not the supported 512 KiB Rolo ROM revision. No files were extracted.', 'Rolo ROM check', 'OK', 'Error') | Out-Null
        exit 2
    }

    New-Item -ItemType Directory -Force $AppDataRoot | Out-Null
    $stage = Join-Path $env:TEMP ('RoloExtract-' + [guid]::NewGuid().ToString('N'))
    $stagedPack = Join-Path $AppDataRoot ('resources-v1-new-' + [guid]::NewGuid().ToString('N'))
    try {
        Write-Host 'The ROM is verified. Extracting the game data for this account…'
        New-Item -ItemType Directory -Force $stage,$stage\assets,$stage\bin,$stage\docs,$stage\local,$stage\migration,$stage\tools | Out-Null
        Copy-Item (Join-Path $Template 'src') (Join-Path $stage 'src') -Recurse
        Copy-Item (Join-Path $Template 'tools\*') (Join-Path $stage 'tools') -Recurse -Force
        Copy-Item (Join-Path $Template 'run_initial_exporters.py'),(Join-Path $Template 'run_array_exporters.py'),(Join-Path $Template 'build_runtime_pack.py'),(Join-Path $Template 'extract_last_runtime_arrays.py'),(Join-Path $Template 'migrate.py'),(Join-Path $Template 'verify_pack.py') $stage
        Copy-Item (Join-Path $Template 'manifest.json') (Join-Path $stage 'migration\manifest.json')
        Copy-Item -LiteralPath $rom -Destination (Join-Path $stage 'local\rolo.md')
        $env:ROLO_PYTHON = $Python
        & $Python (Join-Path $stage 'tools\inventory_rom.py') (Join-Path $stage 'local\rolo.md') --project $stage
        if ($LASTEXITCODE -ne 0) { throw 'ROM inventory failed.' }
        & powershell.exe -NoProfile -File (Join-Path $stage 'tools\Extract-RoloAssets.ps1') -RomPath $rom -OutputDir (Join-Path $stage 'bin')
        if ($LASTEXITCODE -ne 0) { throw 'Asset extraction failed.' }
        & $Python (Join-Path $stage 'tools\export_opening.py') (Join-Path $stage 'local\rolo.md') --project $stage
        if ($LASTEXITCODE -ne 0) { throw 'Opening data extraction failed.' }
        & $Python (Join-Path $stage 'run_initial_exporters.py') $stage
        if ($LASTEXITCODE -ne 0) { throw 'Animation data extraction failed.' }
        & $Python (Join-Path $stage 'run_array_exporters.py') $stage
        if ($LASTEXITCODE -ne 0) { throw 'Runtime table extraction failed.' }
        & $Python (Join-Path $stage 'extract_last_runtime_arrays.py') $stage
        if ($LASTEXITCODE -ne 0) { throw 'Final runtime table extraction failed.' }
        & $Python (Join-Path $stage 'tools\export_direct_runtime_tables.py') $rom (Join-Path $stage 'src') (Join-Path $stage 'migration\manifest.json')
        if ($LASTEXITCODE -ne 0) { throw 'Runtime table verification failed.' }
        & $Python (Join-Path $stage 'build_runtime_pack.py') (Join-Path $stage 'src') (Join-Path $stage 'migration\manifest.json') $stagedPack
        if ($LASTEXITCODE -ne 0) { throw 'Resource pack creation failed.' }
        foreach ($asset in $RequiredAssets) {
            $assetPath = Join-Path (Join-Path $stage 'bin') $asset
            if (!(Test-Path $assetPath)) { throw "Required game asset was not generated: $asset" }
            Copy-Item $assetPath $stagedPack
        }
        & $Python (Join-Path $stage 'verify_pack.py') $stagedPack
        if ($LASTEXITCODE -ne 0) { throw 'Final resource pack verification failed.' }
        $newManifestHash = (Get-FileHash (Join-Path $stagedPack 'manifest.json') -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($newManifestHash -ne $ExpectedManifestSha256) { throw 'The generated pack does not match the pinned game version.' }
        if (Test-Path $DataRoot) {
            Move-Item -LiteralPath $DataRoot -Destination ($DataRoot + '.previous-' + [guid]::NewGuid().ToString('N'))
        }
        Move-Item -LiteralPath $stagedPack -Destination $DataRoot
    }
    catch {
        [System.Windows.Forms.MessageBox]::Show("Rolo could not prepare its data.`r`n`r`n$($_.Exception.Message)", 'Rolo setup failed', 'OK', 'Error') | Out-Null
        exit 1
    }
    finally {
        if (Test-Path $stage) {
            $fullStage = [IO.Path]::GetFullPath($stage)
            $tempRoot = [IO.Path]::GetFullPath($env:TEMP).TrimEnd('\') + '\'
            if ($fullStage.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase)) { Remove-Item -LiteralPath $fullStage -Recurse -Force }
        }
        if (Test-Path $stagedPack) { Remove-Item -LiteralPath $stagedPack -Recurse -Force }
        Remove-Item Env:\ROLO_PYTHON -ErrorAction SilentlyContinue
    }
}

if (!(Test-ReadyPack $DataRoot)) { throw 'The extracted game data did not pass verification.' }
Start-Process -FilePath $Game -WorkingDirectory $AppRoot -ArgumentList @('--resources-ready','--resource-root',('"' + $DataRoot + '"'))

