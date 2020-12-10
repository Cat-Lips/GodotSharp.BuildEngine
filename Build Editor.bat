@ECHO OFF
ECHO Running: %0
POWERSHELL -ExecutionPolicy Bypass env/main.ps1 -editor -mono -update
PAUSE
