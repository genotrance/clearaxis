; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME                         "Clearaxis"
!define PRODUCT_VERSION                      "#VERSION#"
!define PRODUCT_PUBLISHER                    "Ganesh Viswanathan"
!define PRODUCT_WEB_SITE                     "http://www.genotrance.com"
!define PRODUCT_UNINST_KEY                   "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY              "HKLM"

; Output file name of the resulting installer
!define INSTALLER_FILE_NAME                  "clearaxissetup-${PRODUCT_VERSION}.exe"

; Install directory
!define INSTALL_DIRECTORY                    "$PROGRAMFILES\Clearaxis"

; Location of the installation files
!define INSTALLATION_FILES_LOCATION          "dist"

; Location of the documentation files
!define DOCUMENTATION_FILES_LOCATION          "docs"

; Messages
!define ABORT_INSTALL_MESSAGE                 "${PRODUCT_NAME} ${PRODUCT_VERSION} install failed! Aborting installation."
!define ABORT_UNINSTALL_MESSAGE               "${PRODUCT_NAME} ${PRODUCT_VERSION} uninstall failed! Aborting uninstallation."

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Custom page for install options
Page custom EnterInstallOptions ""
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${INSTALLER_FILE_NAME}"
InstallDir "${INSTALL_DIRECTORY}"
ShowInstDetails nevershow
ShowUnInstDetails nevershow

Function .onInit
  InitPluginsDir
  File /oname=$PLUGINSDIR\options.ini options.ini
FunctionEnd

Function EnterInstallOptions
  ; Options dialog
  Push $R0
  InstallOptions::dialog $PLUGINSDIR\options.ini
  Pop $R0

  ; Get selected values
  ReadINIStr $R7 "$PLUGINSDIR\options.ini" "Field 2" "State"
  ReadINIStr $R8 "$PLUGINSDIR\options.ini" "Field 3" "State"
  Push $R7
  Push $R8
FunctionEnd

Section "Installer" SEC01
  ; Close and uninstall older version of AppSnap
  ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString"
  StrCmp $R0 "" uninstalldone
  StrCpy $R1 $R0 -10
  ExecWait '$R0 /S _?=$R1'
  Delete $R0
  uninstalldone:

  ; Copy install files
  SetOutPath "$INSTDIR"
  File "${INSTALLATION_FILES_LOCATION}\*.*"

  ; Copy documentation
  SetOutPath "$INSTDIR\docs"
  File "${DOCUMENTATION_FILES_LOCATION}\*.*"

  ; Copy source
  SetOutPath "$INSTDIR\src"
  File "*.py"
  File "*.ini"
  
  SetOutPath "$INSTDIR"
SectionEnd

Section -Post
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"

  ; Perform install
  Pop $R8
  Pop $R7
  StrCpy $R9 '"$INSTDIR\clearaxis.exe" -install'
  StrCmp $R7 "1" 0 +2
    StrCpy $R9 '$R9 -html_xcompare'
  StrCmp $R8 "1" 0 +2
    StrCpy $R9 '$R9 -xml_xcompare'
  nsExec::ExecToStack '$R9'

  ; Display README
  ExecShell "open" "$INSTDIR\docs\README.txt"
SectionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  ; Uninstall
  nsExec::ExecToStack '"$INSTDIR\clearaxis.exe" -uninstall'

  ; Delete all installed files and directories
  RMDir /r "$INSTDIR\docs"
  RMDir /r "$INSTDIR\src"
  Delete "$INSTDIR\*.*"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  SetAutoClose true
SectionEnd