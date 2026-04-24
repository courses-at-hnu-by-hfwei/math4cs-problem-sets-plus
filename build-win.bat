@echo off
REM build-win.bat -- compile problems.tex with xelatex, convert to README.md, and push
cd /d %~dp0

echo Building PDF (xelatex) - pass 1...
xelatex -interaction=nonstopmode -halt-on-error problems.tex
if errorlevel 1 (
  echo xelatex failed on pass 1.
  exit /b 1
)

echo Building PDF (xelatex) - pass 2...
xelatex -interaction=nonstopmode -halt-on-error problems.tex
if errorlevel 1 (
  echo xelatex failed on pass 2.
  exit /b 1
)

echo Converting TeX to Markdown...
python tex2md.py
if errorlevel 1 (
  echo tex2md.py failed.
  exit /b 1
)

echo Cleaning intermediate files...
del /f /q *.aux *.log *.out *.toc *.lof *.lot *.synctex.gz *.fdb_latexmk *.fls 2>nul

echo Preparing commit...
git add README.md
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-Date).ToString('yyyy-MM-dd_HH-mm-ss')"`) do set TS=%%i
git commit -m "Auto-build: update README.md from problems.tex - %TS%"
if errorlevel 1 (
  echo No changes to commit, skipping push.
  goto :end
)

echo Pushing to remote...
git push

:end
echo Build complete.
exit /b 0
