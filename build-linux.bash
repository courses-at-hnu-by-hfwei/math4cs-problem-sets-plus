#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "Building PDF (xelatex) - pass 1..."
xelatex -interaction=nonstopmode -halt-on-error problems.tex

echo "Building PDF (xelatex) - pass 2..."
xelatex -interaction=nonstopmode -halt-on-error problems.tex

echo "Converting TeX to Markdown..."
if command -v python3 >/dev/null 2>&1; then
  python3 tex2md.py
else
  python tex2md.py
fi

echo "Cleaning intermediate files..."
rm -f *.aux *.log *.out *.toc *.lof *.lot *.synctex.gz *.fdb_latexmk *.fls || true

TS=$(date +"%Y-%m-%d_%H-%M-%S")
echo "Committing README.md (timestamp: $TS)"
git add README.md
if git commit -m "Auto-build: update README.md from problems.tex - $TS"; then
  git push
else
  echo "No changes to commit"
fi

echo "Build complete."
