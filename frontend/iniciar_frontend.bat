@echo off
setlocal
pushd "%~dp0.." || exit /b 1
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" (
  echo Ambiente .venv nao encontrado. Consulte frontend\README.md.
  popd
  exit /b 1
)
"%PY%" -X utf8 -c "import streamlit, pandas, scipy; from frontend import service"
if errorlevel 1 (
  echo Dependencias ausentes ou incompativeis. Consulte frontend\README.md.
  popd
  exit /b 1
)
echo Abrindo PO-RuFaS em http://127.0.0.1:8501
"%PY%" -X utf8 -m streamlit run frontend/app.py %* --server.address 127.0.0.1 --browser.gatherUsageStats false
set "appExit=%errorlevel%"
popd
exit /b %appExit%
