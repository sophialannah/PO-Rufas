@echo off
setlocal
pushd "%~dp0.."
".venv\Scripts\python.exe" -X utf8 -m RUFAS.biophysical.animal.ration.linear_diet_integrated_example %*
set "demoExit=%errorlevel%"
popd
exit /b %demoExit%
