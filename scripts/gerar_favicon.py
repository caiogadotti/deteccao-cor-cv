"""Gera o favicon do app: um objeto detectado com contorno e centroide.

Desenhado com formas vetoriais (PIL), nao gerado por IA -- mesma paleta
escura/ambar do app (--fundo #0a0a0b, --destaque #f5a524).
"""

import os

from PIL import Image, ImageDraw

TAM = 256
FUNDO = "#0a0a0b"
AMBAR = "#f5a524"
BRANCO = "#f4f4f5"

img = Image.new("RGB", (TAM, TAM), FUNDO)
desenho = ImageDraw.Draw(img)
desenho.rounded_rectangle([0, 0, TAM - 1, TAM - 1], radius=48, fill=FUNDO)

# o "objeto" detectado -- retangulo amber com cantos bem arredondados
obj = [72, 64, 184, 192]
desenho.rounded_rectangle(obj, radius=28, fill=AMBAR)

# contorno de deteccao ao redor do objeto (como cv2.drawContours)
margem_contorno = 14
contorno = [obj[0] - margem_contorno, obj[1] - margem_contorno,
            obj[2] + margem_contorno, obj[3] + margem_contorno]
desenho.rounded_rectangle(contorno, radius=36, outline=BRANCO, width=6)

# centroide: circulo + cruz, como cv2.moments marcado no app
cx, cy = (obj[0] + obj[2]) // 2, (obj[1] + obj[3]) // 2
raio = 16
desenho.ellipse([cx - raio, cy - raio, cx + raio, cy + raio], outline=BRANCO, width=6)
desenho.line([cx - 5, cy, cx + 5, cy], fill=BRANCO, width=5)
desenho.line([cx, cy - 5, cx, cy + 5], fill=BRANCO, width=5)

destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "favicon.png")
img.save(destino)
print("salvo em", os.path.relpath(destino))
