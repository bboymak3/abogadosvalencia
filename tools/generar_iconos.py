#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera los iconos del sitio (favicon SVG/PNG, apple-touch-icon, 192, 512 y
maskable) con el mismo logotipo "AV" dorado sobre negro del menú.

Uso:
    python3 tools/generar_iconos.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "assets", "icons")
DORADO = (212, 175, 55)
NEGRO = (0, 0, 0)
FUENTES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#000"/>
  <rect x="6" y="6" width="52" height="52" rx="10" fill="#D4AF37"/>
  <text x="32" y="42" text-anchor="middle" font-family="-apple-system, Segoe UI, Arial, sans-serif" font-size="26" font-weight="800" fill="#000">AV</text>
</svg>
"""


def fuente(tam):
    for f in FUENTES:
        if os.path.exists(f):
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


def icono(tam, margen_seguro=False, redondeado=True):
    img = Image.new("RGBA", (tam, tam), NEGRO + (255,) if (margen_seguro or not redondeado) else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if not margen_seguro and redondeado:
        d.rounded_rectangle([0, 0, tam - 1, tam - 1], radius=int(tam * 0.22), fill=NEGRO)
    # Zona segura del icono "maskable": el contenido ocupa el 80 % central
    interior = 0.62 if margen_seguro else 0.82
    lado = int(tam * interior)
    x0 = (tam - lado) // 2
    d.rounded_rectangle([x0, x0, x0 + lado, x0 + lado], radius=int(lado * 0.18), fill=DORADO)
    f = fuente(int(lado * 0.46))
    caja = d.textbbox((0, 0), "AV", font=f)
    w, h = caja[2] - caja[0], caja[3] - caja[1]
    d.text(((tam - w) / 2 - caja[0], (tam - h) / 2 - caja[1]), "AV", font=f, fill=NEGRO)
    return img


def main():
    os.makedirs(DESTINO, exist_ok=True)
    with open(os.path.join(DESTINO, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(SVG)
    icono(32).save(os.path.join(DESTINO, "favicon-32.png"))
    icono(192).save(os.path.join(DESTINO, "icon-192.png"))
    icono(512).save(os.path.join(DESTINO, "icon-512.png"))
    icono(512, margen_seguro=True).save(os.path.join(DESTINO, "icon-maskable-512.png"))
    # iOS no admite transparencia en el apple-touch-icon: fondo opaco
    icono(180, redondeado=False).convert("RGB").save(os.path.join(DESTINO, "apple-touch-icon.png"))
    print("Iconos generados en", os.path.relpath(DESTINO, RAIZ))


if __name__ == "__main__":
    main()
