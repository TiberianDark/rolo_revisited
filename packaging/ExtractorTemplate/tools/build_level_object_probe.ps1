$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Path 'outputs/rolo-native/local/object-audit' -Force | Out-Null
$vs='C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools'
$lines=& cmd.exe /d /c "`"$vs\Common7\Tools\VsDevCmd.bat`" -arch=x64 -host_arch=x64 >nul && set"
foreach($line in $lines){if($line -match '^([^=]+)=(.*)$'){[Environment]::SetEnvironmentVariable($matches[1],$matches[2],'Process')}}
& cl.exe /nologo /std:c++20 /EHsc /O2 /I outputs/rolo-native/src outputs/rolo-native/tests/level_object_probe.cpp /Fe:outputs/rolo-native/local/object-audit/level_object_probe.exe /Fo:outputs/rolo-native/local/object-audit/level_object_probe.obj *> outputs/rolo-native/local/object-audit/build.log
if($LASTEXITCODE){Get-Content outputs/rolo-native/local/object-audit/build.log -Tail 20;throw 'Compile failed'}
