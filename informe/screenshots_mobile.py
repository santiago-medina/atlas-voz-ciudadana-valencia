"""Capturas en viewport móvil para detectar problemas de responsividad."""

import asyncio
from pathlib import Path

OUT = Path(__file__).resolve().parent / "screenshots" / "mobile"
OUT.mkdir(parents=True, exist_ok=True)

URL = "https://santiago-medina.github.io/atlas-voz-ciudadana-valencia/"


async def main() -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # iPhone 13 mini viewport
        ctx = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        )
        page = await ctx.new_page()

        print(f"→ Cargando {URL} en viewport 390×844 (iPhone)")
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_selector("text=Atlas de la Voz Ciudadana")
        await page.wait_for_timeout(2500)

        # 1. Portada
        await page.screenshot(path=OUT / "01_portada.png", full_page=False)
        print("   01_portada.png")

        # 2. Scroll progresivo
        await page.evaluate("window.scrollTo(0, 600)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / "02_hallazgo_central.png", full_page=False)
        print("   02_hallazgo_central.png")

        await page.evaluate("window.scrollTo(0, 1300)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / "03_como_funciona.png", full_page=False)
        print("   03_como_funciona.png")

        await page.evaluate("window.scrollTo(0, 2200)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / "04_mapa_inicio.png", full_page=False)
        print("   04_mapa_inicio.png")

        await page.evaluate("window.scrollTo(0, 3500)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / "05_mapa_y_significado.png", full_page=False)
        print("   05_mapa_y_significado.png")

        # 3. Full page para inspección completa
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / "00_full.png", full_page=True)
        print("   00_full.png")

        await browser.close()

    print("\nResultado:")
    for f in sorted(OUT.glob("*.png")):
        print(f"  {f.name}  {f.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    asyncio.run(main())
