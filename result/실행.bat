@echo off
setlocal

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%..\backend

echo 백엔드 서버를 새 창에서 띄웁니다...
start "혹시 백엔드" cmd /k "cd /d %BACKEND_DIR% && call .venv\Scripts\activate.bat && python app.py"

echo 서버가 준비될 때까지 기다립니다...
powershell -NoProfile -Command "$ok=$false; for ($i=0; $i -lt 30; $i++) { try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/health' -UseBasicParsing -TimeoutSec 1; if ($r.StatusCode -eq 200) { $ok=$true; break } } catch {} Start-Sleep -Milliseconds 700 }; if (-not $ok) { Write-Host '서버 응답이 없어요. 새로 뜬 [혹시 백엔드] 콘솔 창에 에러가 있는지 확인해주세요.' }"

echo 결과 화면을 엽니다...
start "" "%SCRIPT_DIR%index.html"

endlocal
