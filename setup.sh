#!/usr/bin/env bash
# Cloud environment setup script. Paste this into the routine's environment
# settings (Edit routine -> environment -> Setup script). The result is cached,
# so it does not re-run on every session.
set -euo pipefail

pip install --break-system-packages -q \
  yfinance polars pandas pyarrow numpy matplotlib requests

python - <<'PY'
import matplotlib, yfinance, polars, pyarrow
print("deps ok:", matplotlib.__version__, yfinance.__version__, polars.__version__)
PY
