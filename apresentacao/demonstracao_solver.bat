@echo off
setlocal
chcp 65001 >nul
pushd "%~dp0.." || exit /b 1
if not exist ".venv\Scripts\python.exe" (
  echo Ambiente .venv nao encontrado. Consulte apresentacao\guia_demonstracao.md.
  popd
  exit /b 1
)
set PYTHONUTF8=1
".venv\Scripts\python.exe" -m apresentacao.demo_solver %*
set "demo_exit=%errorlevel%"
popd
exit /b %demo_exit%
