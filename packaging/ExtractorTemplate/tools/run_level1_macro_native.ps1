$ErrorActionPreference='Stop'
$project=Split-Path $PSScriptRoot -Parent
$build=Join-Path $project 'local/macro-audit'
New-Item -ItemType Directory -Path $build -Force | Out-Null
$vs='C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools'
if(-not (Test-Path -LiteralPath (Join-Path $vs 'Common7/Tools/VsDevCmd.bat'))){throw 'Visual C++ Build Tools were not found; static audit still works without a compiler.'}
$lines=& cmd.exe /d /c "`"$vs\Common7\Tools\VsDevCmd.bat`" -arch=x64 -host_arch=x64 >nul && set"
foreach($line in $lines){if($line -match '^([^=]+)=(.*)$'){[Environment]::SetEnvironmentVariable($matches[1],$matches[2],'Process')}}
$source=Join-Path $project 'tests/level1_macro_audit.cpp'
$exe=Join-Path $build 'level1_macro_audit.exe'
& cl.exe /nologo /std:c++20 /EHsc /O2 /I (Join-Path $project 'src') $source ('/Fe:'+$exe) ('/Fo:'+(Join-Path $build 'level1_macro_audit.obj')) *> (Join-Path $build 'build.log')
if($LASTEXITCODE){throw ('Native macro audit compile failed; see '+$build+'\build.log')}
$output=& $exe
if($LASTEXITCODE){$output | Set-Content -Encoding utf8 (Join-Path $build 'result.json');throw 'Native macro audit reported a failure'}
$output | Set-Content -Encoding utf8 (Join-Path $build 'result.json')
Write-Output $output
