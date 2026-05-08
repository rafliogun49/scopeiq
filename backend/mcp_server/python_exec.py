"""python_exec MCP tool — interface contract §7.3."""

import asyncio
import base64
import io
import os
import platform
import sys
import tempfile
import textwrap


# Import yang diizinkan di dalam sandbox
ALLOWED_IMPORTS = {
    "pandas",
    "numpy",
    "matplotlib",
    "json",
    "math",
    "statistics",
    "collections",
    "itertools",
    "functools",
    "re",
    "datetime",
}

SANDBOX_SCRIPT = textwrap.dedent("""
import sys, json, base64, io

# Inject dataset dari env
import os
dataset_json = os.environ.get("DATASET_JSON", "{}")

# Sediakan variabel 'data' untuk user code
import json as _json
data = _json.loads(dataset_json)

# Tangkap matplotlib charts
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_charts = []
_orig_savefig = plt.savefig

def _capture_savefig(fname=None, *args, **kwargs):
    buf = io.BytesIO()
    plt.savefig(buf, format="png", *args, **kwargs)
    buf.seek(0)
    _charts.append(base64.b64encode(buf.read()).decode())

plt.savefig = _capture_savefig

# Jalankan user code
import sys as _sys
_stdout = io.StringIO()
_sys.stdout = _stdout

try:
{user_code}
finally:
    _sys.stdout = sys.__stdout__

print(json.dumps({{
    "stdout": _stdout.getvalue(),
    "charts": _charts,
}}))
""")


async def python_exec(code: str, dataset_id: str) -> dict:
    """Jalankan code Python di subprocess sandbox. Returns {{stdout, charts}}."""

    # Indent user code supaya masuk ke dalam script wrapper
    indented = textwrap.indent(code, "    ")
    script = SANDBOX_SCRIPT.format(user_code=indented)

    # Tulis ke temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        tmp_path = f.name

    try:
        env = os.environ.copy()
        env["DATASET_JSON"] = dataset_id  # dataset_id berisi JSON string dari Redis

        # Linux: gunakan unshare -n untuk isolasi network
        # macOS (dev): langsung python saja
        if platform.system() == "Linux":
            cmd = ["unshare", "-n", sys.executable, tmp_path]
        else:
            cmd = [sys.executable, tmp_path]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
        except asyncio.TimeoutError:
            proc.kill()
            return {"stdout": "", "charts": [], "error": "Timeout: eksekusi melebihi 30 detik"}

        if proc.returncode != 0:
            return {
                "stdout": "",
                "charts": [],
                "error": stderr.decode()[:500],
            }

        import json

        result = json.loads(stdout.decode())
        return result

    finally:
        os.unlink(tmp_path)
