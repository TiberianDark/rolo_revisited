$ErrorActionPreference='Stop'
$project=Split-Path $PSScriptRoot
$workspace=Split-Path (Split-Path $project)
Push-Location $workspace
try {
 $vs='C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools'
 $lines=& cmd.exe /d /c "`"$vs\Common7\Tools\VsDevCmd.bat`" -arch=x64 -host_arch=x64 >nul && set"
 foreach($line in $lines){if($line -match '^([^=]+)=(.*)$'){[Environment]::SetEnvironmentVariable($matches[1],$matches[2],'Process')}}
 & cl.exe /nologo /std:c++20 /EHsc /O2 /MT /I outputs/rolo-native/src /I outputs/rolo-native/tests outputs/rolo-native/tools/offline_assignment_checker.cpp '/Fe:outputs/rolo-native/Check Level Assignments.exe' /Fo:work/offline-assignment-checker.obj /link bcrypt.lib shell32.lib *> work/offline-assignment-checker-build.log
 if($LASTEXITCODE){Get-Content work/offline-assignment-checker-build.log -Tail 18;throw 'Offline checker compilation failed'}
}finally{Pop-Location}

