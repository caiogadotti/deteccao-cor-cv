<div align="center">

# Color-Based Position Detector

**Visual perception for a cyber-physical system: from camera to decision.**

A computer vision pipeline that detects a colored object in an image and
classifies its position, left, center or right, using only OpenCV and
NumPy, no machine learning involved.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

[Português](README.md) &nbsp;·&nbsp; **English**

</div>

![Pipeline in action: input, HSV mask and result classified as CENTER](docs/pipeline_exemplo.png)

---

## The problem

Before any automated decision, a cyber-physical system needs to perceive the
world. This project solves the simplest step of that loop: given an image,
locate where an object is and translate that into a discrete decision.

> Input: a color image. Output: a command among **ESQUERDA** (left),
> **CENTRO** (center), **DIREITA** (right) or **SEM_DETECCAO** (no
> detection), based on the horizontal position of the largest object of the
> chosen color.

This loop, perception then decision, is the foundation of any real
cyber-physical system: a cart following a lane, a robotic arm locating a
part, a drone avoiding obstacles. Here it is solved the simplest way
possible, color thresholding, before any more sophisticated model enters
the picture in later classes.

---

## Running it

```bash
git clone https://github.com/caiogadotti/deteccao-cor-cv.git
cd deteccao-cor-cv
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. No dataset and no training step:
the pipeline runs directly on whatever image you feed it.

---

## What the app does

**Three ways to feed it an image, one active at a time.** Take a photo
through the browser webcam, upload an image from your computer, or generate
a synthetic test image when no camera is available. The same problem the
professor solved in the demonstration script, adapted inside the app.
Switching modes actually turns the camera off: only the widget for the
selected mode stays mounted on the page, so the webcam does not keep
running hidden behind another tab.

**Live calibration.** Four preset colors (green, blue, red, yellow) or a
manual mode with hue (H), saturation (S) and brightness (V) sliders. HSV
calibration is sensitive to lighting, which is why the assignment asks to
test under at least two different lighting conditions.

**Show why.** The result is not just a label: the annotated image shows the
detected contour and centroid, and a separate section shows the binary mask
used to get there. You can see exactly what the algorithm saw.

**Target color coverage.** Besides the largest contour's area, the app
shows what fraction of the whole image fell inside the color range. When
that coverage goes above 60%, a warning appears: the algorithm is likely
picking up the scene's background, not an isolated object.

---

## The pipeline

The same five steps from the `aula01_camera.ipynb` notebook, isolated in
`src/deteccao.py` as a pure function, testable outside Streamlit:

```
BGR image -> convert to HSV -> thresholding (cv2.inRange)
          -> largest contour (cv2.findContours) -> centroid (cv2.moments)
          -> classification by horizontal position
```

| Step | Function | Why |
|---|---|---|
| BGR to HSV | `cv2.cvtColor` | Separating color from brightness is easier in HSV than in RGB. The same color under strong or weak light falls in the same hue range |
| Thresholding | `cv2.inRange` | Creates a binary mask: white where the pixel falls inside the color range |
| Contours | `cv2.findContours` | Finds the connected regions of white pixels in the mask |
| Centroid | `cv2.moments` | Computes the center of mass of the largest contour, the point that represents "where the object is" |
| Classification | comparison with tolerance | Compares the horizontal position of the centroid against the frame's midpoint, using a tolerance band so it does not flicker between CENTER and LEFT/RIGHT over a single pixel |

**Why a tolerance band instead of comparing directly against the exact
midpoint:** without it, an object 1 pixel off center would flip between
LEFT and RIGHT with every small camera or object vibration. The band
creates a stable "CENTER" zone in the middle of the frame.

**Why a minimum area:** without this filter, noise in the mask (a handful
of isolated pixels that happened to fall in the color range) becomes a
detected "object". Requiring a minimum area discards that noise.

---

## Project structure

```
├── app.py                Streamlit app
├── src/
│   └── deteccao.py        detection pipeline, isolated and testable
├── requirements.txt
└── docs/
```

---

## Assignment checklist (Class 1)

- [x] The camera opens without errors (via `st.camera_input`, through the browser)
- [x] The frame is displayed with the result overlaid
- [x] Detection works under more than one condition: manual calibration
      (H/S/V sliders) allows retuning without touching code when lighting changes
- [x] The decision rule is implemented and commented (`src/deteccao.py`)
- [x] Repository with `README.md` and `requirements.txt`
- [x] Camera-less fallback, to test the pipeline without depending on hardware

---

## Stack

| Library | Role |
|---|---|
| **OpenCV** | Color conversion, thresholding, contours, moments |
| **NumPy** | Image arrays and color ranges |
| **Pillow** | Bridge between Streamlit's image format and OpenCV's |
| **Streamlit** | Web interface |

---

## Credits

**Course:** Computational Laboratory of Machine Learning (LCML), 2026/2
**Class:** CIB-NA8
**Professor:** Reinaldo Augusto de Oliveira Ramos
