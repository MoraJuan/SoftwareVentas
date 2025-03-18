; Script de instalación para DiagSoft
; Creado con NSIS (Nullsoft Scriptable Install System)

!define APPNAME "DiagSoft"
!define COMPANYNAME "DiagSoft"
!define DESCRIPTION "Sistema de ventas e inventario"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://www.diagsoft.com/help"
!define UPDATEURL "https://www.diagsoft.com/update"
!define ABOUTURL "https://www.diagsoft.com/about"

; Nombre del archivo de salida del instalador
OutFile "DiagSoft_Setup.exe"

; Directorio de instalación predeterminado
InstallDir "$PROGRAMFILES\${APPNAME}"

; Solicitar privilegios de administrador
RequestExecutionLevel admin

; Variables
Var StartMenuFolder

; Página de bienvenida
!insertmacro MUI_PAGE_WELCOME

; Página de licencia (opcional, descomentare y añadir su archivo de licencia)
; !insertmacro MUI_PAGE_LICENSE "licencia.txt"

; Página de instalación
!insertmacro MUI_PAGE_INSTFILES

; Página de finalización
!insertmacro MUI_PAGE_FINISH

; Incluir configuraciones modernas de UI
!include "MUI2.nsh"

; Nombre del instalador
Name "${APPNAME}"

; Idioma del instalador
!insertmacro MUI_LANGUAGE "Spanish"

; Sección principal de instalación
Section "Instalación principal" SecInstall
    SetOutPath "$INSTDIR"
    
    ; Archivos a incluir en el instalador
    File "DiagSoft.exe"
    File "ventas.db"
    
    ; Crear directorio para datos
    CreateDirectory "$INSTDIR\data"
    
    ; Crear acceso directo en el menú de inicio
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\DiagSoft.exe"
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\DiagSoft.exe"
    
    ; Escribir información de desinstalación en el registro
    WriteUninstaller "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\DiagSoft.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    
    ; Estimar el tamaño de la instalación
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"
SectionEnd

; Sección de desinstalación
Section "Uninstall"
    ; Eliminar accesos directos
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$DESKTOP\${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    ; Eliminar archivos de la instalación
    Delete "$INSTDIR\DiagSoft.exe"
    Delete "$INSTDIR\ventas.db"
    Delete "$INSTDIR\uninstall.exe"
    
    ; Preguntar si desea conservar los datos
    MessageBox MB_YESNO|MB_ICONQUESTION "¿Desea conservar los datos de la aplicación? Seleccione 'Sí' para mantener la base de datos y configuraciones." IDYES KeepData
    
    ; Eliminar directorios de datos si el usuario eligió no conservarlos
    RMDir /r "$INSTDIR\data"
    Goto Continue
    
    KeepData:
    DetailPrint "Los datos de la aplicación se han conservado."
    
    Continue:
    ; Eliminar directorio de instalación
    RMDir "$INSTDIR"
    
    ; Eliminar claves del registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd

; Funciones
Function .onInit
    ; Configuraciones iniciales
    InitPluginsDir
    
    ; Verificar si ya está instalado
    ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString"
    StrCmp $R0 "" done
    
    ; Preguntar si desea desinstalar la versión anterior
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION "${APPNAME} ya está instalado. $\n$\nHaga clic en 'Aceptar' para eliminar la versión anterior o en 'Cancelar' para cancelar esta instalación." IDOK uninst
    Abort
    
    uninst:
    ; Ejecutar el desinstalador
    ClearErrors
    ExecWait '$R0 _?=$INSTDIR'
    
    ; Verificar errores
    IfErrors no_remove_uninstaller done
    no_remove_uninstaller:
    
    done:
FunctionEnd 