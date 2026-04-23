; PyFyve Installer Script
; Place this file in the project root alongside start.bat
; Compile with Inno Setup: https://jrsoftware.org/isinfo.php
;
; Before compiling:
;   1. Put your icon at assets\icon.ico
;   2. Run the compiler — no other changes needed

#define MyAppName "PyFyve"
#define MyAppVersion "1.0.0"
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

; installer_output\ is gitignored — the compiled .exe lands here
OutputDir=installer_output
OutputBaseFilename=PyFyve_Setup_v1.0.0
SolidCompression=yes
WizardStyle=slate

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; All paths relative to the project root where this .iss file lives.
; Excludes: git history, venv, pycache, user files, model files (downloaded at runtime),
; and the installer output folder itself.
Source: "*"; DestDir: "{app}"; \
    Excludes: ".git\*,.venv\*,__pycache__\*,user_progress.json,user_workspace.py,model\*,installer_output\*,*.iss,*.gif,*.png"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu entry
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon.ico"
; Desktop shortcut (optional, unchecked by default)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\assets\icon.ico"
; Uninstaller in Start Menu
Name: "{autoprograms}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
; Offer to launch immediately after install completes
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; \
    Flags: shellexec postinstall skipifsilent; \
    WorkingDir: "{app}"

[UninstallDelete]
; Remove files generated during normal use that the uninstaller won't catch automatically.
; model\ is handled by the [Code] section below (user has a choice).
Type: filesandordirs; Name: "{app}\.venv"
Type: filesandordirs; Name: "{app}\src\__pycache__"
Type: files;          Name: "{app}\user_progress.json"
Type: files;          Name: "{app}\user_workspace.py"
Type: dirifempty;     Name: "{app}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    // Always deregister the model from Ollama.
    //
    // 'ollama rm fyve-ai' does two things:
    //   1. Removes the model from Ollama's registry.
    //   2. Deletes Ollama's internal blob copy (~2.5 GB in ~/.ollama/models/).
    //
    // This runs unconditionally so no ghost model is left in Ollama after
    // PyFyve is removed. The source GGUF in {app}\model\ is handled separately
    // below — if the user keeps those files, reinstalling PyFyve re-registers
    // the model from them with no internet download required.
    Exec('cmd.exe', '/c ollama rm fyve-ai', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    // Ask separately about the source GGUF files PyFyve downloaded.
    // These are independent of Ollama's internal copy and take up ~2.6 GB.
    // Keeping them makes reinstalling PyFyve faster (no re-download needed).
    if MsgBox(
      'Do you also want to delete PyFyve''s downloaded model files?' + #13#10#13#10 +
      'Yes  — deletes the source model files (~2.6 GB freed).' + #13#10 +
      'No   — keeps them so reinstalling PyFyve requires no re-download.',
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      // IsDir=True, DeleteFiles=True, DeleteSubDirs=True — wipes everything inside model\
      DelTree(ExpandConstant('{app}\model'), True, True, True);
    end;
  end;
end;
