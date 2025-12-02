@echo off
REM Server Management Batch Script for Windows
REM Usage: manage_servers.bat [start|stop|restart|status]

if "%1"=="" (
    echo Usage: manage_servers.bat [start^|stop^|restart^|status]
    echo.
    echo Commands:
    echo   start   - Start all servers (excluding speech-to-text)
    echo   stop    - Stop all running servers
    echo   restart - Restart all servers
    echo   status  - Check server status
    exit /b 1
)

cd /d "%~dp0"
python manage_servers.py %1

