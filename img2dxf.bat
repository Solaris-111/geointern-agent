@echo off
chcp 65001 >nul
title 图片转DXF

if "%~1"=="" (
    echo ========================================
    echo   图片转 DXF 工具
    echo   把 JPG/PNG/BMP 图片拖到这个 bat 上即可
    echo ========================================
    pause
    exit /b
)

powershell -ExecutionPolicy Bypass -File "D:\geointern-agent\img2dxf.ps1" "%~1"
pause
