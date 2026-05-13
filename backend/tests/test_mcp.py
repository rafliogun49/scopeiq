"""MCP smoke test — B-PR2.
Acceptance: python_exec menghasilkan valid base64 PNG dari matplotlib.
"""

import base64

import pytest

from mcp_server.python_exec import python_exec


@pytest.mark.asyncio
async def test_python_exec_returns_png():
    """python_exec dengan matplotlib harus return base64 PNG."""
    code = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

competitors = ['Tool A', 'Tool B', 'Tool C']
prices = [9, 29, 49]

plt.figure(figsize=(6, 4))
plt.bar(competitors, prices, color='steelblue')
plt.title('Competitor Pricing')
plt.ylabel('Price ($/month)')
plt.savefig('chart.png')
"""
    result = await python_exec(code=code, dataset_id="{}")

    # Harus return dict dengan key charts
    assert isinstance(result, dict), "Result harus berupa dict"
    assert "charts" in result, "Result harus punya key 'charts'"
    assert len(result["charts"]) >= 1, "Harus ada minimal 1 chart PNG"

    # Validasi base64
    chart_b64 = result["charts"][0]
    decoded = base64.b64decode(chart_b64)
    assert len(decoded) > 0, "PNG tidak boleh kosong"

    # Validasi PNG header (magic bytes: \x89PNG)
    assert decoded[:4] == b"\x89PNG", "File harus valid PNG"

    print(f"✅ PNG valid — size: {len(decoded)} bytes")


@pytest.mark.asyncio
async def test_python_exec_stdout():
    """python_exec harus capture stdout."""
    code = "print('hello from sandbox')"
    result = await python_exec(code=code, dataset_id="{}")
    assert "hello from sandbox" in result.get("stdout", "")
    print("✅ stdout captured correctly")
