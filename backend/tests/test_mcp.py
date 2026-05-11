"""MCP smoke test — B-PR2.
Acceptance: python_exec menghasilkan valid base64 PNG.
"""

import base64

import pytest

from mcp_server.python_exec import python_exec


@pytest.mark.asyncio
async def test_python_exec_returns_png():
    """python_exec dengan matplotlib harus return base64 PNG."""
    code = """
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

    # Harus ada key charts
    assert "charts" in result, "Result harus punya key 'charts'"

    # Harus ada minimal 1 chart
    assert len(result["charts"]) >= 1, "Harus ada minimal 1 chart PNG"

    # Harus valid base64
    chart_b64 = result["charts"][0]
    try:
        decoded = base64.b64decode(chart_b64)
        assert len(decoded) > 0, "Base64 PNG tidak boleh kosong"
    except Exception:
        pytest.fail("Chart bukan valid base64 string")

    print(f"✅ PNG size: {len(decoded)} bytes")


@pytest.mark.asyncio
async def test_python_exec_stdout():
    """python_exec harus capture stdout."""
    code = "print('hello from sandbox')"
    result = await python_exec(code=code, dataset_id="{}")
    assert "hello from sandbox" in result.get("stdout", "")
