; —————————————————————————————
; SortBench v1.1 - Sorting Benchmark Application Installer
; Developed by Anurag Chattopadhyay
; —————————————————————————————
[Setup]
; Basic Information
AppName=SortBench
AppVersion=1.1.0
AppPublisher=Anurag Chattopadhyay
DefaultDirName={autopf}\SortBench
DefaultGroupName=SortBench
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=SortBench_v1.1_Setup
SetupIconFile=benchmark.ico
WizardSmallImageFile=benchmark.bmp
WizardImageFile=benchmark_finish.bmp
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
AppId={{31879BEB-DC2D-40F8-A678-8CEF3ABDDA71}}
UninstallDisplayIcon={app}\SortBench.exe
UninstallDisplayName=SortBench - Sorting Benchmark Application
VersionInfoVersion=1.1.0.0
VersionInfoCompany=Anurag Chattopadhyay
VersionInfoDescription=SortBench - Sorting Algorithm Benchmarking Tool (intended for educational and research purposes)
VersionInfoProductName=SortBench
VersionInfoProductVersion=1.1.0
VersionInfoCopyright=© 2025 Anurag Chattopadhyay

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";      Description: "{cm:CreateDesktopIcon}";        GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon";  Description: "{cm:CreateQuickLaunchIcon}";   GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked;

[Files]
Source: "dist\SortBench.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "benchmark.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SortBench";                                          Filename: "{app}\SortBench.exe"; IconFilename: "{app}\benchmark.ico"
Name: "{group}\{cm:UninstallProgram,SortBench}";                    Filename: "{uninstallexe}"
Name: "{autodesktop}\SortBench";                                    Filename: "{app}\SortBench.exe"; IconFilename: "{app}\benchmark.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\SortBench"; Filename: "{app}\SortBench.exe"; IconFilename: "{app}\benchmark.ico"; Tasks: quicklaunchicon;

[Run]
Filename: "{app}\SortBench.exe"; Description: "{cm:LaunchProgram,SortBench}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\SortBench"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\SortBench"; ValueType: string; ValueName: "Version"; ValueData: "1.1.0"; Flags: uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// —————————————————————————————
// Custom Welcome Page with Disclaimer
// —————————————————————————————
var
  DisclaimerPage: TOutputMsgMemoWizardPage;

procedure InitializeWizard;
var
  InfoText: String;
begin
  InfoText :=
            'SortBench v1.1 - Sorting Algorithm Benchmarking Tool' + #13#10#13#10 +
            'This tool provides comprehensive benchmarking and comparison of sorting algorithms (intended for educational and research purposes).' + #13#10#13#10 +
            'Key Features:' + #13#10 +
            '->  9 Built-in sorting algorithms with custom sorting algorithm and dataset support' + #13#10 +
            '->  Multiple test states (Original, Random, Nearly-Sorted, Sorted, Reverse-Sorted)' + #13#10 +
            '->  Execution logs with export option (TXT, PDF)' + #13#10 +
            '->  Performance charts with export option (PNG)' + #13#10 +
            '->  Tabulated data with export option (CSV, Excel)' + #13#10 +
            '->  (Planned Future Update) Oracle DB integration to store benchmark output data' + #13#10#13#10 +
            'System Requirements:' + #13#10 +
            '->  Windows 10/11 (64-bit)' + #13#10 +
            '->  Minimum 4GB RAM (8GB recommended)' + #13#10 +
            '->  1GB free disk space' + #13#10#13#10 +
            'Click Next to continue with the installation.';
  
  DisclaimerPage := CreateOutputMsgMemoPage(
    wpWelcome,
    'Welcome to SortBench v1.1 Installer',
    'Developed by Anurag Chattopadhyay',
    '',       // SubCaption (optional)
    InfoText  // MemoText
  );
  
  // Make the memo read-only and non-focusable
  DisclaimerPage.RichEditViewer.ReadOnly := True;
  DisclaimerPage.RichEditViewer.TabStop := False;
end;