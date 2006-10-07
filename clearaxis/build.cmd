@echo off

:: Version
set VERSION=1.01

::Set personal Path to the Apps:
set PythonEXE=D:\Mess\Python24\python.exe
set SevenZipEXE=D:\Mess\Progra~1\SevenZip\7z.exe
set UpxEXE=D:\Windows\upx.exe
set NSIS=D:\Mess\Progra~1\NSIS\makensis.exe

::Check existance of files
if not exist clearaxis.py         call FileNotFound clearaxis.py
if not exist %PythonEXE%          call FileNotFound %PythonEXE%
if not exist %SevenZipEXE%        call FileNotFound %SevenZipEXE%
if not exist %UpxEXE%             call FileNotFound %UpxEXE%

::Write the Py2EXE-Setup File
call :MakeSetupFile >"clearaxis_EXESetup.py"

::Compile the Python-Script
%PythonEXE% -OO "clearaxis_EXESetup.py" py2exe
if not "%errorlevel%"=="0" (
        echo Py2EXE Error!
        pause
        goto eof
)

:: Delete the Py2EXE-Setup File
del "clearaxis_EXESetup.py"

:: Copy the Py2EXE Results to the SubDirectory and Clean Py2EXE-Results
rd build /s /q
xcopy dist\*.* "clearaxis_EXE\" /d /y
rd dist /s /q

:: Compress the files
call :CompressFiles
call :Package
echo.
echo.
echo Done: "clearaxis_EXE\"
echo.
pause
goto eof

:: Compression
:CompressFiles
        cd clearaxis_EXE
        %UpxEXE% --best *.*
		cd..
goto eof

:: Package
:Package
		del clearaxissetup-%VERSION%.exe

		%NSIS% clearaxissetup.nsi
goto eof

:: Generate the setup file
:MakeSetupFile
        echo.
        echo from distutils.core import setup
        echo import py2exe
        echo.
        echo setup (
        echo    console = [{
        echo       "script"         : "clearaxis.py"
        echo    }],
        echo    options = {
        echo       "py2exe": {
        echo          "packages" : ["encodings"],
        echo          "optimize" : 2,
        echo          "compressed" : 1,
        echo          "bundle_files" : 2
        echo       }
        echo    },
        echo    zipfile = None)
        echo.
goto eof

:: Errors
:FileNotFound
        echo.
        echo Error, File not found:
        echo [%1]
        echo.
        echo Check Path in %~nx0???
        echo.
        pause
        exit
goto eof

:eof