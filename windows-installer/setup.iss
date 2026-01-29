; Inno Setup Script for Password Generator
; 使用 Inno Setup 6.x 编译此脚本生成安装程序
; 下载 Inno Setup: https://jrsoftware.org/isdl.php

#define MyAppName "Password Generator"
#define MyAppNameCN "密码生成器"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "zhuyikai2002"
#define MyAppURL "https://github.com/zhuyikai2002/password-generator"
#define MyAppExeName "PasswordGenerator.hta"

[Setup]
; 应用信息
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases

; 安装目录
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; 输出设置
OutputDir=output
OutputBaseFilename=PasswordGenerator-{#MyAppVersion}-Setup
SetupIconFile=files\icon.ico
Compression=lzma2
SolidCompression=yes

; 权限
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; 界面设置
WizardStyle=modern
WizardSizePercent=100

; 语言
[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式(&D)"; GroupDescription: "附加图标:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "创建快速启动栏图标(&Q)"; GroupDescription: "附加图标:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; 主程序文件
Source: "files\PasswordGenerator.hta"; DestDir: "{app}"; Flags: ignoreversion
Source: "files\pwgen.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "files\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 开始菜单
Name: "{group}\{#MyAppNameCN}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\卸载 {#MyAppNameCN}"; Filename: "{uninstallexe}"
; 桌面快捷方式
Name: "{autodesktop}\{#MyAppNameCN}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
; 快速启动
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppNameCN}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: quicklaunchicon

[Run]
; 安装完成后运行
Filename: "{app}\{#MyAppExeName}"; Description: "立即运行 {#MyAppNameCN}"; Flags: nowait postinstall skipifsilent shellexec

[Code]
// 自定义安装完成页面文本
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    WizardForm.FinishedLabel.Caption := '安装程序已在您的计算机上安装了 密码生成器。' + #13#10 + #13#10 +
      '您可以通过桌面快捷方式或开始菜单启动应用程序。';
  end;
end;
