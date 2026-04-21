; BookUnbind Windows installer (Inno Setup 6)
;
; Version is injected by CI:
;   iscc /DAppVersion=0.2.4 installer\BookUnbind.iss
; If not supplied, defaults to 0.0.0 for local test builds.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

#define AppName       "BookUnbind"
#define AppPublisher  "RuData"
#define AppURL        "https://github.com/swiftruru/book-unbind"
#define AppExeName    "BookUnbind.exe"
; SourceDir is where `flet build windows` produced the app (relative to this .iss)
#define SourceDir     "..\build\windows"

[Setup]
AppId={{A0B1C2D3-4E5F-4A7B-9C0D-BKUNBIND00001}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
DisableDirPage=no
; Per-user install to avoid UAC elevation prompts
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=BookUnbind-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName} {#AppVersion}
; Branding: setup.exe icon + wizard graphics
SetupIconFile=..\assets\icon.ico
WizardImageFile=wizard_image.bmp
WizardSmallImageFile=wizard_small.bmp
WizardImageStretch=yes
; Avoid the "run from a network share" failure mode entirely by forbidding
; install destinations on network / shared drives (e.g. C:\Mac\... on Parallels).
; Inno Setup can't directly detect Prl SF, but installing to %LocalAppData%
; or Program Files by default already sidesteps it.

[Languages]
; Inno Setup 6.7 only ships a handful of official languages; ChineseTraditional
; is community-maintained and not bundled, so we keep the installer UI in
; English. The app itself remains zh-TW.
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
