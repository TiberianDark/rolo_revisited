param([Parameter(Mandatory=$true)][ValidateSet('level1_enemy_slice_tests','level1_objects_tests','level1_transport_world_tests')][string]$Check)
$ErrorActionPreference='Stop'
$project=Split-Path $PSScriptRoot -Parent
$build=Join-Path $project 'local/gameplay-checks'
New-Item -ItemType Directory -Path $build -Force | Out-Null
$vs='C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools'
if(-not (Test-Path -LiteralPath (Join-Path $vs 'Common7/Tools/VsDevCmd.bat'))){throw 'Visual C++ Build Tools were not found.'}
$lines=& cmd.exe /d /c "`"$vs\Common7\Tools\VsDevCmd.bat`" -arch=x64 -host_arch=x64 >nul && set"
foreach($line in $lines){if($line -match '^([^=]+)=(.*)$'){[Environment]::SetEnvironmentVariable($matches[1],$matches[2],'Process')}}
$exe=Join-Path $build ($Check+'.exe')
& cl.exe /nologo /std:c++20 /EHsc /O2 /F16777216 /I (Join-Path $project 'src') (Join-Path $project ('tests/'+$Check+'.cpp')) ('/Fe:'+$exe) ('/Fo:'+(Join-Path $build ($Check+'.obj'))) *> (Join-Path $build ($Check+'-build.log'))
if($LASTEXITCODE){throw ('Compile failed; see '+$build+'\'+$Check+'-build.log')}
& $exe *> (Join-Path $build ($Check+'-run.log'))
if($LASTEXITCODE){throw ('Check failed; see '+$build+'\'+$Check+'-run.log')}
Write-Output ($Check+': passed')
