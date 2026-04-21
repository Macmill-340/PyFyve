; PyFyve Installer Script
; Place this file in the project root alongside start.bat
; Compile with Inno Setup: https://jrsoftware.org/isinfo.php
;
; Before compiling:
;   1. Put your icon at assets\icon.ico
;   2. Set OutputDir below to wherever you want the final .exe
;   3. Run the compiler — no other changes needed

#define MyAppName "PyFyve"
#define MyAppVersion "1.0"
#define MyAppPublisher "Macmill-340"
#define MyAppURL "https://github.com/Macmill-340/PyFyve"
#define MyAppExeName "start.bat"

[Setup]
AppId={{DD641EC2-906A-41E4-82CD-E5720CCFF2F9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installs to %LOCALAPPDATA%\PyFyve — no admin rights required
DefaultDirName={localappdata}\{#MyAppName}
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DisableProgramGroupPage=yes

; Paths are relative to this .iss file (project root)
LicenseFile=LICENSE.md
InfoBeforeFile=assets\installer_info.rtf
SetupIconFile=assets\icon.ico

; Change this to wherever you want the output .exe written
; {src} = the folder this .iss file lives in
OutputDir=installer_output
OutputBaseFilename=PyFyve_Setup_v1.0

SolidCompression=yes
WizardStyle=slate

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; All paths relative to the project root where this .iss file lives
; Excludes: git history, venv, pycache, and user-generated runtime files
Source: "*"; DestDir: "{app}"; \
    Excludes: ".git\*,.venv\*,__pycache__\*,user_progress.json,user_workspace.py,model\*,installer_output\*,*.iss"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
[Icons]
; Start Menu entry
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon.ico"

; Desktop shortcut (optional, unchecked by default)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\assets\icon.ico"

; Uninstaller in Start Menu
Name: "{autoprograms}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
; Offer to launch immediately after install
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; \
    Flags: shellexec postinstall skipifsilent; \
    WorkingDir: "{app}"

[UninstallDelete]
; Clean up files generated during normal use that the uninstaller won't catch
Type: filesandordirs; Name: "{app}\.venv"
Type: filesandordirs; Name: "{app}\src\__pycache__"
Type: files;          Name: "{app}\user_progress.json"
Type: files;          Name: "{app}\user_workspace.py"
; model\ is handled by the prompt in [Code] below
Type: dirifempty;     Name: "{app}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    if MsgBox(
      'Do you also want to delete the downloaded AI model?' + #13#10#13#10 +
      'Yes  — removes the model (~2.5 GB freed).' + #13#10 +
      'No   — keeps the model so reinstalling PyFyve is faster.',
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Unload from Ollama registry first, then delete the files
      Exec('cmd.exe', '/c ollama rm fyve-ai', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      DelTree(ExpandConstant('{app}\model'), True, True, True);
    end;
  end;
end;
