@ECHO OFF
RMDIR /S /Q __pycache__ /S /Q build /S /Q dist
DEL calendar_with_ui.spec
pyinstaller --noconsole calendar_with_ui.py
copy data.dat /B dist\calendar_with_ui\data.dat /B
copy settings.txt dist\calendar_with_ui\settings.txt
robocopy default dist\calendar_with_ui\default /E