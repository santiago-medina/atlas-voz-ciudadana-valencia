"""
build_informe.py — Construye el informe PDF a partir del Markdown.

Inserta los 13 hallazgos generados por 10_hallazgos.py dentro de la sección
correspondiente del informe.md, y compila con pandoc.
"""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INF = ROOT / "informe"
PROC = ROOT / "data" / "processed"


def build_hallazgos_md(hallazgos: list[dict]) -> str:
    parts = []
    for h in hallazgos:
        parts.append(f"### {h['id']} · {h['titulo']}")
        parts.append("")
        parts.append(f"> **{h['cifra']}**")
        parts.append("")
        parts.append(h["texto"])
        parts.append("")
        parts.append(f"*Fuente: {h['fuente']}*")
        parts.append("")
    return "\n".join(parts)


def main() -> None:
    md = (INF / "informe.md").read_text(encoding="utf-8")
    hallazgos = json.loads((PROC / "hallazgos.json").read_text(encoding="utf-8"))
    md = md.replace("{HALLAZGOS}", build_hallazgos_md(hallazgos))

    out_md = INF / "_informe_built.md"
    out_md.write_text(md, encoding="utf-8")

    html = INF / "_informe_built.html"
    pdf = INF / "informe.pdf"

    # 1. Markdown -> HTML con pandoc (sin LaTeX)
    css = INF / "informe.css"
    subprocess.run(
        [
            "pandoc",
            str(out_md),
            "-o",
            str(html),
            "--toc",
            "--toc-depth=2",
            "--number-sections",
            "--standalone",
            "--metadata=title:Atlas de la Voz Ciudadana de València",
            "--css",
            str(css),
        ],
        check=True,
    )
    print(f"  HTML generado: {html.name}")

    # 2. HTML -> PDF con wkhtmltopdf
    subprocess.run(
        [
            "wkhtmltopdf",
            "--enable-local-file-access",
            "--encoding",
            "utf-8",
            "--margin-top",
            "22mm",
            "--margin-bottom",
            "22mm",
            "--margin-left",
            "20mm",
            "--margin-right",
            "20mm",
            "--footer-center",
            "[page] · Atlas de la Voz Ciudadana de València",
            "--footer-font-size",
            "8",
            "--footer-spacing",
            "5",
            str(html),
            str(pdf),
        ],
        check=True,
    )
    print(f"  PDF generado: {pdf} ({pdf.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
