"""Pipeline de detecção de posição por cor (percepção do sistema ciber-físico).

Segue exatamente os passos da Aula 1: BGR -> HSV -> limiarização -> contornos
-> centro de massa -> classificação de posição (ESQUERDA / CENTRO / DIREITA).

Isolado do app.py para poder ser testado sozinho e reaproveitado num script
de captura contínua depois (integração com o microcontrolador, aulas 6-7).
"""

from dataclasses import dataclass

import cv2
import numpy as np

PRESETS_COR = {
    "Verde": ((40, 50, 50), (80, 255, 255)),
    "Azul": ((90, 60, 60), (130, 255, 255)),
    "Vermelho": ((0, 70, 50), (10, 255, 255)),
    "Amarelo": ((20, 70, 70), (35, 255, 255)),
}


@dataclass
class ResultadoDeteccao:
    comando: str
    area: float
    centro: tuple | None
    mascara: np.ndarray
    contorno: np.ndarray | None


def detectar_posicao(
    frame_bgr: np.ndarray,
    cor_baixa: tuple,
    cor_alta: tuple,
    area_minima: int = 500,
    margem_centro: int = 80,
) -> ResultadoDeteccao:
    """Roda o pipeline completo em UM frame e devolve o comando de posição.

    Mesma lógica do notebook `aula01_camera.ipynb` (passo 5), extraída para
    função pura -- funciona tanto num loop de vídeo quanto numa imagem única.
    """
    altura, largura = frame_bgr.shape[:2]
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, np.array(cor_baixa), np.array(cor_alta))

    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contornos:
        return ResultadoDeteccao("SEM_DETECCAO", 0.0, None, mascara, None)

    maior = max(contornos, key=cv2.contourArea)
    area = cv2.contourArea(maior)

    if area <= area_minima:
        return ResultadoDeteccao("SEM_DETECCAO", area, None, mascara, None)

    momentos = cv2.moments(maior)
    if momentos["m00"] == 0:
        return ResultadoDeteccao("SEM_DETECCAO", area, None, mascara, None)

    cx = int(momentos["m10"] / momentos["m00"])
    cy = int(momentos["m01"] / momentos["m00"])
    centro_frame = largura // 2

    if cx < centro_frame - margem_centro:
        comando = "ESQUERDA"
    elif cx > centro_frame + margem_centro:
        comando = "DIREITA"
    else:
        comando = "CENTRO"

    return ResultadoDeteccao(comando, area, (cx, cy), mascara, maior)


def desenhar_resultado(frame_bgr: np.ndarray, resultado: ResultadoDeteccao, cor_bgr: tuple) -> np.ndarray:
    """Desenha o contorno, o centro e o rótulo do comando sobre uma cópia do frame."""
    saida = frame_bgr.copy()

    if resultado.contorno is not None:
        cv2.drawContours(saida, [resultado.contorno], -1, cor_bgr, 2)
    if resultado.centro is not None:
        cv2.circle(saida, resultado.centro, 20, cor_bgr, 3)

    cv2.putText(
        saida, resultado.comando, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.4, cor_bgr, 3
    )
    return saida
