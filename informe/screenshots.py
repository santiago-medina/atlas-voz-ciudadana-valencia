"""
screenshots.py — Capturas estáticas de la web desplegada con Playwright.

Genera 4 imágenes para anexar al expediente o usar en el vídeo demo:

  01_portada.png         — vista inicial sin tema seleccionado
  02_tema_aceras.png     — mapa coloreado por 'Aceras y movilidad peatonal'
  03_campanar_ficha.png  — ficha del distrito Campanar abierta
  04_hallazgos.png       — sección de 13 hallazgos
"""

import asyncio
from pathlib import Path

OUT = Path(__file__).resolve().parent / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

URL = "https://santiago-medina.github.io/atlas-voz-ciudadana-valencia/"


async def main() -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
        page = await ctx.new_page()

        print(f"→ Cargando {URL}")
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_selector("text=Atlas de la Voz Ciudadana")
        await page.wait_for_timeout(2500)

        # 1. Portada
        await page.screenshot(path=OUT / "01_portada.png", full_page=False)
        print("   01_portada.png")

        # 2. Tema seleccionado: usar el value real del <option>
        # Buscamos qué option contiene "Aceras y movilidad peatonal"
        target_value = await page.evaluate(
            """
            (() => {
              const sel = document.querySelector('select');
              if (!sel) return null;
              const opt = Array.from(sel.options).find(o => o.text.includes('Aceras y movilidad peatonal'));
              return opt ? opt.value : null;
            })()
            """
        )
        if target_value:
            await page.select_option("select", value=target_value)
        await page.wait_for_timeout(1800)
        await page.screenshot(path=OUT / "02_tema_aceras.png", full_page=False)
        print("   02_tema_aceras.png")

        # 3. Click sobre Campanar (más sencillo: usar coordenadas conocidas o
        #    buscar feature por texto del tooltip). Usamos click en el centro
        #    aproximado del distrito en el mapa.
        # Coordenadas aproximadas del centroide de Campanar en pantalla a 1600x1000:
        # mejor: buscamos por js que dispare click en el path correspondiente
        # Click sobre el polígono de Campanar. Leaflet añade los handlers a
        # cada path SVG; busco el path que al pasarle el ratón muestra
        # 'Campanar' en el tooltip, leo su bounding box y hago click real.
        target_box = await page.evaluate(
            """
            (() => {
              const paths = Array.from(document.querySelectorAll('.leaflet-interactive'));
              for (const p of paths) {
                p.dispatchEvent(new Event('mouseover', {bubbles: true}));
              }
              // After mouseovers, Leaflet creates tooltips; pick the path whose
              // tooltip contains 'Campanar' from bound layers via data-attrs.
              // Fallback: choose the path centered roughly over Campanar's
              // coordinates by approximating bounding box positions.
              return null;
            })()
            """
        )
        # Robust approach: use page.evaluate to call Leaflet API directly
        clicked = await page.evaluate(
            """
            (() => {
              // Find the React state setter via the global Leaflet map ref
              // Easier: programmatically dispatch the React click handler.
              // The map listens via Leaflet's GeoJSON onEachFeature → layer.on('click').
              // We can fire Leaflet's click on the matching layer.
              try {
                const mapEl = document.querySelector('.leaflet-container');
                if (!mapEl || !mapEl._leaflet_id) return false;
                // Walk Leaflet maps registry
                const mapId = mapEl._leaflet_id;
                const L = window.L;
                if (!L) return false;
                // L stores maps in L.Map._map cache (not standard). Fallback:
                // iterate panes and find a layer with feature.properties.nombre_distrito === 'Campanar'.
                const panes = document.querySelectorAll('.leaflet-overlay-pane svg path');
                for (const p of panes) {
                  if (!p.__layer) continue;
                  const feat = p.__layer.feature;
                  if (feat && feat.properties && feat.properties.nombre_distrito === 'Campanar') {
                    p.__layer.fire('click');
                    return true;
                  }
                }
                return false;
              } catch (e) { return false; }
            })()
            """
        )
        if not clicked:
            # As a last resort, click the SVG path at Campanar's geographic
            # position. Campanar centroid is roughly at lat 39.487, lng -0.405.
            # We use Leaflet's latLngToContainerPoint via map ref if accessible,
            # otherwise approximate from viewport: Campanar is in the NW.
            await page.mouse.click(720, 380)
        await page.wait_for_timeout(1800)
        # Scroll a bit so the ficha is visible
        await page.evaluate("window.scrollBy(0, 600)")
        await page.wait_for_timeout(500)

        await page.screenshot(path=OUT / "03_campanar_ficha.png", full_page=False)
        print("   03_campanar_ficha.png")

        # 4. Sección hallazgos: scroll
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight - 1200)")
        await page.wait_for_timeout(800)
        await page.screenshot(path=OUT / "04_hallazgos.png", full_page=False)
        print("   04_hallazgos.png")

        # 5. Full page
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / "05_full_page.png", full_page=True)
        print("   05_full_page.png")

        await browser.close()

    print("\nResultado:")
    for f in sorted(OUT.glob("*.png")):
        print(f"  {f.name}  {f.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    asyncio.run(main())
