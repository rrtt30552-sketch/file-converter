@echo off
chcp 65001 >nul
echo ========================================
echo   万能文件转换工具 - 打包脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.10+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 安装依赖
echo 📦 安装依赖...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo 🔨 开始打包...
pyinstaller --onefile --windowed ^
    --name "文件转换工具" ^
    --icon=icon.ico ^
    --add-data "converter;converter" ^
    --noconfirm ^
    --clean ^
    gui.py

echo.
if exist "dist\文件转换工具.exe" (
    echo ✅ 打包成功！
    echo 📄 输出文件: dist\文件转换工具.exe
    echo.
    echo 你可以把这个 exe 复制到桌面双击使用！
) else (
    echo ❌ 打包失败，请检查错误信息
)

echo.
pause
