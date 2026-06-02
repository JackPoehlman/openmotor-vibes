#define MyAppExeName "openMotorVibes.exe"
#define DistRoot AddBackslash(SourcePath) + "..\\dist\\openMotorVibes"

[Setup]
AppName=OpenMotor Vibes
AppVersion=0.6.1
WizardStyle=modern
DefaultDirName={autopf}\OpenMotor Vibes
DefaultGroupName=OpenMotor Vibes
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
ChangesAssociations=yes

[Files]
Source: "{#DistRoot}\\*"; DestDir: "{app}"; Flags: recursesubdirs; Excludes: "*installer*.exe,mysetup.exe"

[Icons]
Name: "{group}\OpenMotor Vibes"; Filename: "{app}\{#MyAppExeName}"

[Registry]
; Associate .ric files with OpenMotor Vibes
Root: HKA; Subkey: "Software\Classes\.ric\OpenWithProgids"; ValueType: string; ValueName: "openMotorVibes.ric"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\openMotorVibes.ric"; ValueType: string; ValueName: ""; ValueData: "OpenMotor Vibes Motor File"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\openMotorVibes.ric\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\_internal\resources\oMFile256.ico"
Root: HKA; Subkey: "Software\Classes\openMotorVibes.ric\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".ric"; ValueData: ""
