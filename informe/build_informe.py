"""
build_informe.py — Construye los PDFs del proyecto (informe técnico + memoria
resumen) a partir de Markdown. Pipeline:

    pandoc --standalone --toc → HTML temporal
    wkhtmltopdf               → PDF final con tipografía editorial

Inserta los 13 hallazgos generados por 10_hallazgos.py donde aparece el
marcador {HALLAZGOS} en informe.md.
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


def build_one(md_path: Path, pdf_path: Path, html_path: Path, *, css_path: Path) -> None:
    md = md_path.read_text(encoding="utf-8")
    if "{HALLAZGOS}" in md:
        hallazgos = json.loads((PROC / "hallazgos.json").read_text(encoding="utf-8"))
        md = md.replace("{HALLAZGOS}", build_hallazgos_md(hallazgos))
    built_md = md_path.with_name(f"_built_{md_path.stem}.md")
    built_md.write_text(md, encoding="utf-8")
    subprocess.run(
        ["pandoc", str(built_md), "-o", str(html_path), "--toc", "--toc-depth=2",
         "--number-sections", "--standalone", "--css", str(css_path)],
        check=True,
    )
    subprocess.run(
        ["wkhtmltopdf", "--enable-local-file-access", "--encoding", "utf-8",
         "--margin-top", "22mm", "--margin-bottom", "22mm",
         "--margin-left", "20mm", "--margin-right", "20mm",
         str(html_path), str(pdf_path)],
        check=True,
    )
    print(f"  PDF: {pdf_path.name}  ({pdf_path.stat().st_size/1024:.1f} KB)")


def main() -> None:
    css = INF / "informe.css"
    build_one(INF / "informe.md", INF / "informe.pdf", INF / "_informe_built.html", css_path=css)
    build_one(INF / "MEMORIA_RESUMEN.md", INF / "MEMORIA_RESUMEN.pdf", INF / "_memoria_built.html", css_path=css)


if __name__ == "__main__":
    main()
