"""Detector de posição por cor -- interface Streamlit.

Rodar:
    streamlit run app.py
"""

import os
import sys

import cv2
import numpy as np
import streamlit as st
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.deteccao import PRESETS_COR, desenhar_resultado, detectar_posicao


def gerar_imagem_simulada(posicao: str) -> Image.Image:
    """Retângulo verde sintético, no lugar da câmera quando ela não está disponível.

    Mesma ideia do fallback que o professor deu em aula: se não tem câmera,
    testa o pipeline com uma imagem sintética em vez de travar o experimento.
    """
    imagem = np.zeros((480, 640, 3), dtype=np.uint8)
    x0 = {"ESQUERDA": 60, "CENTRO": 260, "DIREITA": 460}[posicao]
    cv2.rectangle(imagem, (x0, 140), (x0 + 120, 340), (0, 255, 0), -1)
    cv2.putText(
        imagem, "SIMULACAO", (180, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )
    return Image.fromarray(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))

st.set_page_config(
    page_title="Detector de Posição por Cor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ESTILO = """
<style>
:root {
    --fundo: #0a0a0b;
    --superficie: #131316;
    --superficie-alta: #1b1b20;
    --borda: #292930;
    --texto: #f4f4f5;
    --texto-suave: #8b8b96;
    --texto-fraco: #5a5a66;
    --destaque: #f5a524;
    --destaque-claro: #fbca6d;
    --verde: #7dd3a8;
    --azul: #7aa2f7;
    --vermelho: #f37272;
}

.stApp { background: var(--fundo); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.2rem 3rem 4rem; max-width: 1240px; }

.marca {
    display: block;
    color: var(--destaque); font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 0.7rem;
}

h1.titulo {
    color: var(--texto); font-size: 2.7rem; font-weight: 700;
    letter-spacing: -0.035em; line-height: 1.05; margin: 0 0 0.6rem;
}
.chamada { color: var(--texto-suave); font-size: 1rem; line-height: 1.6; max-width: 60ch; }
.chamada strong { color: var(--texto); font-weight: 600; }

.faixa-metricas { display: flex; gap: 2.4rem; margin: 1.8rem 0 2.2rem; flex-wrap: wrap; }
.metrica-valor {
    font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
    color: var(--destaque); font-size: 1.6rem; font-weight: 600; line-height: 1;
}
.metrica-rotulo {
    color: var(--texto-fraco); font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 0.1em; margin-top: 0.35rem;
}

.painel {
    background: var(--superficie); border: 1px solid var(--borda);
    border-radius: 14px; padding: 1.4rem;
}
.painel-titulo {
    color: var(--texto-fraco); font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.9rem;
}

.leitura {
    font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
    font-size: 2.4rem; font-weight: 700; line-height: 1.1; text-align: center;
    margin: 0.6rem 0 0.2rem; white-space: nowrap;
}
.leitura-rotulo {
    text-align: center; color: var(--texto-fraco); font-size: 0.7rem;
    text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 1.4rem;
}
.leitura-vazia {
    font-family: ui-monospace, monospace; font-size: 3.6rem; font-weight: 700;
    line-height: 1; text-align: center; color: var(--superficie-alta);
    margin: 0.6rem 0 0.2rem;
}

.info-linha { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--borda); }
.info-linha:last-child { border-bottom: none; }
.info-chave { color: var(--texto-fraco); font-size: 0.85rem; }
.info-valor { color: var(--texto); font-size: 0.85rem; font-family: ui-monospace, monospace; font-weight: 600; }

.legenda { text-align: center; color: var(--texto-fraco); font-size: 0.68rem; margin-top: 0.4rem; }

button[data-testid="stBaseButton-segmented_control"] {
    background: var(--superficie-alta) !important;
    border: 1px solid var(--borda) !important;
    color: var(--texto-suave) !important;
    font-weight: 600 !important;
}
button[data-testid="stBaseButton-segmented_controlActive"] {
    background: var(--destaque) !important;
    border-color: var(--destaque) !important;
    color: #131316 !important;
}
button[data-testid="stBaseButton-segmented_controlActive"] p { color: #131316 !important; }

div[data-testid="stFileUploaderDropzone"], div[data-testid="stCameraInput"] video {
    background: var(--superficie-alta); border: 1.5px dashed var(--borda); border-radius: 12px;
}

div[data-testid="stExpander"] {
    border: 1px solid var(--borda); border-radius: 12px; background: var(--superficie);
}
div[data-testid="stExpander"] summary { color: var(--texto-suave); font-size: 0.85rem; }

.rodape {
    color: var(--texto-fraco); font-size: 0.72rem; text-align: center;
    margin-top: 3rem; padding-top: 1.6rem; border-top: 1px solid var(--borda);
}
</style>
"""

st.markdown(ESTILO, unsafe_allow_html=True)

CORES_COMANDO = {
    "ESQUERDA": ("#f5a524", (36, 165, 245)),
    "DIREITA": ("#7aa2f7", (247, 162, 122)),
    "CENTRO": ("#7dd3a8", (168, 211, 125)),
    "SEM_DETECCAO": ("#f37272", (114, 114, 243)),
}


def num(valor, casas=0):
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def pil_para_bgr(imagem_pil: Image.Image) -> np.ndarray:
    rgb = np.array(imagem_pil.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def bgr_para_pil(frame_bgr: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))


st.markdown('<div class="marca">LCML · Sistemas Ciber-Físicos</div>', unsafe_allow_html=True)
st.markdown('<h1 class="titulo">Detector de posição<br>por cor</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="chamada">Tire uma foto ou envie uma imagem. O pipeline converte para HSV, '
    "isola a cor-alvo, encontra o maior contorno e classifica a posição do objeto: "
    "<strong>ESQUERDA</strong>, <strong>CENTRO</strong> ou <strong>DIREITA</strong>.</p>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="faixa-metricas">
        <div>
            <div class="metrica-valor">HSV</div>
            <div class="metrica-rotulo">espaço de cor usado</div>
        </div>
        <div>
            <div class="metrica-valor">cv2</div>
            <div class="metrica-rotulo">findContours + moments</div>
        </div>
        <div>
            <div class="metrica-valor">4</div>
            <div class="metrica-rotulo">classes de posição</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Calibração (cor-alvo, área mínima, margem)", expanded=True):
    col_cor, col_area, col_margem = st.columns(3)

    with col_cor:
        preset = st.selectbox("Cor-alvo", list(PRESETS_COR.keys()) + ["Personalizado"])

        if preset == "Personalizado":
            h_min, h_max = st.slider("Matiz (H)", 0, 179, (40, 80))
            s_min = st.slider("Saturação mínima (S)", 0, 255, 50)
            v_min = st.slider("Brilho mínimo (V)", 0, 255, 50)
            cor_baixa, cor_alta = (h_min, s_min, v_min), (h_max, 255, 255)
        else:
            cor_baixa, cor_alta = PRESETS_COR[preset]
            st.markdown(
                f'<p class="legenda" style="text-align:left; margin-top:0.4rem;">'
                f"H {cor_baixa[0]}–{cor_alta[0]} · S ≥ {cor_baixa[1]} · V ≥ {cor_baixa[2]}</p>",
                unsafe_allow_html=True,
            )

    with col_area:
        area_minima = st.slider("Área mínima (px²)", 100, 5000, 500, step=100)
        st.markdown(
            '<p class="legenda" style="text-align:left;">Contornos menores que isso '
            "são ignorados (ruído).</p>",
            unsafe_allow_html=True,
        )

    with col_margem:
        margem = st.slider("Margem do centro (px)", 20, 200, 80, step=10)
        st.markdown(
            '<p class="legenda" style="text-align:left;">Faixa ao redor do meio da imagem '
            "classificada como CENTRO.</p>",
            unsafe_allow_html=True,
        )

col_entrada, col_resultado = st.columns([1, 1], gap="large")

with col_entrada:
    st.markdown('<div class="painel-titulo">Entrada</div>', unsafe_allow_html=True)

    modo = st.segmented_control(
        "Modo de entrada",
        ["Câmera", "Enviar imagem", "Sem câmera"],
        default="Câmera",
        label_visibility="collapsed",
    )
    imagem_pil = None

    # só o widget do modo selecionado é instanciado -- ao trocar de modo, o
    # st.camera_input anterior é removido da árvore e o navegador libera a
    # câmera de verdade, em vez de ficar ligada escondida atrás de uma aba
    if modo == "Câmera":
        foto = st.camera_input("Tirar foto", label_visibility="collapsed")
        if foto is not None:
            imagem_pil = Image.open(foto)

    elif modo == "Enviar imagem":
        arquivo = st.file_uploader(
            "Imagem", type=["png", "jpg", "jpeg"], label_visibility="collapsed"
        )
        if arquivo is not None:
            imagem_pil = Image.open(arquivo)
            st.image(imagem_pil, use_container_width=True)
        else:
            st.markdown(
                '<p style="color:#6b7590; text-align:center; padding: 2.5rem 0;">'
                "Arraste uma imagem ou clique para selecionar</p>",
                unsafe_allow_html=True,
            )

    elif modo == "Sem câmera":
        st.markdown(
            '<p class="legenda" style="margin-bottom:0.8rem;">Sem webcam disponível? '
            "Gera um quadrado verde sintético na posição escolhida, para testar o pipeline "
            "sem depender de câmera.</p>",
            unsafe_allow_html=True,
        )
        posicao_simulada = st.radio(
            "Posição do objeto simulado", ["ESQUERDA", "CENTRO", "DIREITA"], horizontal=True
        )
        imagem_pil = gerar_imagem_simulada(posicao_simulada)
        st.image(imagem_pil, use_container_width=True)

with col_resultado:
    st.markdown('<div class="painel">', unsafe_allow_html=True)
    st.markdown('<div class="painel-titulo">Resultado</div>', unsafe_allow_html=True)

    if imagem_pil is not None:
        frame_bgr = pil_para_bgr(imagem_pil)
        resultado = detectar_posicao(frame_bgr, cor_baixa, cor_alta, area_minima, margem)

        cor_css, cor_bgr = CORES_COMANDO[resultado.comando]
        anotado = desenhar_resultado(frame_bgr, resultado, cor_bgr)

        st.markdown(
            f'<div class="leitura" style="color:{cor_css};">{resultado.comando}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="leitura-rotulo">comando classificado</div>', unsafe_allow_html=True)

        st.image(bgr_para_pil(anotado), use_container_width=True)

        st.markdown(
            f"""
            <div style="margin-top:1rem;">
                <div class="info-linha"><span class="info-chave">Cobertura da cor-alvo</span>
                    <span class="info-valor">{num(resultado.cobertura_percentual, 1)}% da imagem</span></div>
                <div class="info-linha"><span class="info-chave">Área do contorno</span>
                    <span class="info-valor">{num(resultado.area)} px²</span></div>
                <div class="info-linha"><span class="info-chave">Centro detectado</span>
                    <span class="info-valor">{resultado.centro if resultado.centro else "—"}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if resultado.cobertura_percentual > 60:
            st.markdown(
                '<p class="legenda" style="color:#f5a524; text-align:left; margin-top:0.6rem;">'
                "⚠ Mais da metade da imagem tem essa cor — provavelmente é o fundo da cena, "
                "não um objeto isolado.</p>",
                unsafe_allow_html=True,
            )

        with st.expander("Ver máscara HSV"):
            st.image(resultado.mascara, use_container_width=True, clamp=True)
            st.markdown(
                '<p class="legenda">Branco = pixels dentro do intervalo de cor definido na calibração.</p>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="leitura-vazia">—</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="leitura-rotulo">aguardando uma imagem</div>', unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

with st.expander("Como o pipeline funciona"):
    st.markdown(
        '<p class="nota" style="color:#8b8b96; font-size:0.85rem; line-height:1.6;">'
        "1. A imagem BGR é convertida para o espaço <strong>HSV</strong>, onde separar cor de "
        "brilho é mais fácil que em RGB.<br>"
        "2. <code>cv2.inRange()</code> cria uma máscara binária: branco onde o pixel está dentro "
        "do intervalo de cor, preto no resto.<br>"
        "3. <code>cv2.findContours()</code> encontra as regiões conectadas na máscara; ficamos "
        "com a maior.<br>"
        "4. <code>cv2.moments()</code> calcula o centro de massa (centroide) do contorno.<br>"
        "5. Comparamos a posição horizontal do centro com o meio da imagem, usando uma margem "
        "de tolerância, para decidir ESQUERDA, CENTRO ou DIREITA.</p>",
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="rodape">OpenCV · NumPy · Streamlit &nbsp;|&nbsp; '
    "Aula 1 &nbsp;|&nbsp; LCML Engenharia de Sistemas Ciber-Físicos 2026</div>",
    unsafe_allow_html=True,
)
