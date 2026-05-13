from __future__ import annotations

import sys
import threading
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lsc_alphabet.config import DEFAULT_MODEL_PATH, MODELS_DIR
from lsc_alphabet.landmarks import create_hands, extract_landmark_result
from lsc_alphabet.predictor import GesturePredictor
from lsc_alphabet.sequences import build_sequence_feature_vector
from lsc_alphabet.stabilizer import PredictionStabilizer
from lsc_alphabet.visualization import draw_landmarks, draw_overlay

try:
    import av
    from streamlit_webrtc import RTCConfiguration, VideoProcessorBase, WebRtcMode, webrtc_streamer

    WEBRTC_AVAILABLE = True
except Exception:
    WEBRTC_AVAILABLE = False
    av = None
    VideoProcessorBase = object


st.set_page_config(
    page_title="Traductor LSC",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #f7f8fb;
        color: #18202b;
    }
    .block-container {
        padding-top: 1.2rem;
        max-width: 1240px;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #dfe5ee;
        border-radius: 8px;
        padding: 14px 16px;
        min-height: 88px;
    }
    .metric-card .label {
        color: #5b6573;
        font-size: 0.82rem;
        margin-bottom: 6px;
    }
    .metric-card .value {
        color: #151c27;
        font-size: 1.35rem;
        font-weight: 700;
        overflow-wrap: anywhere;
    }
    .status-ok {
        color: #0f7b55;
        font-weight: 700;
    }
    .status-warn {
        color: #9a5b00;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_predictor(model_path: str) -> GesturePredictor:
    return GesturePredictor.from_file(model_path)


class LSCVideoProcessor(VideoProcessorBase):
    def __init__(
        self,
        model_path: str,
        confidence_threshold: float,
        stable_frames: int,
        mirror_camera: bool,
    ) -> None:
        self.lock = threading.Lock()
        self.model_path = model_path
        self.predictor = None
        self.hands = None
        self.stabilizer = PredictionStabilizer(
            stable_frames=stable_frames,
            confidence_threshold=confidence_threshold,
        )
        self.sequence_length = 6
        self.sequence_buffer: deque[np.ndarray] = deque(maxlen=self.sequence_length)
        self.mirror_camera = mirror_camera
        self.latest_label = ""
        self.latest_confidence = 0.0
        self.latest_text = ""

    def _ensure_initialized(self) -> None:
        if self.predictor is not None and self.hands is not None:
            return

        # Defer heavy initialization to avoid WebRTC signaling timeouts.
        with self.lock:
            if self.predictor is None:
                self.predictor = GesturePredictor.from_file(self.model_path)
                self.sequence_length = int(self.predictor.sequence_length or 6)
                self.sequence_buffer = deque(maxlen=self.sequence_length)
            if self.hands is None:
                self.hands = create_hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=0.65,
                    min_tracking_confidence=0.65,
                )

    def recv(self, frame):  # type: ignore[override]
        self._ensure_initialized()
        image_bgr = frame.to_ndarray(format="bgr24")
        if self.mirror_camera:
            image_bgr = cv2.flip(image_bgr, 1)

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        landmark_result = extract_landmark_result(image_rgb, self.hands)
        prediction = None
        if landmark_result is not None:
            if self.predictor.model_type == "sequence":
                self.sequence_buffer.append(landmark_result.feature_vector)
                if len(self.sequence_buffer) == self.sequence_length:
                    sequence_features = build_sequence_feature_vector(list(self.sequence_buffer))
                    prediction = self.predictor.predict_features(sequence_features)
            else:
                prediction = self.predictor.predict_features(landmark_result.feature_vector)

        self.stabilizer.update_from_prediction(prediction)

        draw_landmarks(image_bgr, landmark_result)
        draw_overlay(
            image_bgr,
            prediction,
            text=self.stabilizer.text,
            status="Espacio/borrar/limpiar desde los controles laterales",
        )

        with self.lock:
            self.latest_label = prediction.display_label if prediction else ""
            self.latest_confidence = prediction.confidence if prediction else 0.0
            self.latest_text = self.stabilizer.text

        return av.VideoFrame.from_ndarray(image_bgr, format="bgr24")

    def space(self) -> None:
        with self.lock:
            self.stabilizer.space()
            self.latest_text = self.stabilizer.text

    def delete(self) -> None:
        with self.lock:
            self.stabilizer.delete()
            self.latest_text = self.stabilizer.text

    def clear(self) -> None:
        with self.lock:
            self.stabilizer.clear()
            self.sequence_buffer.clear()
            self.latest_text = self.stabilizer.text


def render_metric(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_setup_message() -> None:
    st.markdown("### Modelo no encontrado")
    st.code(
        """python scripts/build_dataset.py --input data/raw data/external --output data/processed/features.csv
python scripts/train_model.py --features data/processed/features.csv
streamlit run app.py""",
        language="powershell",
    )


def process_snapshot(predictor: GesturePredictor, uploaded_image) -> None:
    if predictor.model_type == "sequence":
        st.warning("El modelo cargado es temporal; usa la pestaña Camara para reconocer una secuencia.")
        return

    bytes_data = uploaded_image.getvalue()
    array = np.frombuffer(bytes_data, np.uint8)
    image_bgr = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image_bgr is None:
        st.error("No se pudo leer la imagen.")
        return

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    with create_hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.65) as hands:
        prediction, landmark_result = predictor.predict_image(image_rgb, hands)

    draw_landmarks(image_bgr, landmark_result)
    draw_overlay(image_bgr, prediction, text=prediction.display_label if prediction else "")
    st.image(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)

    if prediction:
        render_metric("Prediccion", f"{prediction.display_label} - {prediction.confidence:.0%}")
    else:
        st.warning("No se detecto una mano en la imagen.")


def main() -> None:
    model_candidates = sorted(MODELS_DIR.glob("*.joblib"))
    if model_candidates:
        model_labels = [str(path) for path in model_candidates]
        default_index = 0
        if DEFAULT_MODEL_PATH in model_candidates:
            default_index = model_candidates.index(DEFAULT_MODEL_PATH)
        selected_model = st.sidebar.selectbox("Modelo", model_labels, index=default_index)
        model_path = Path(selected_model)
    else:
        model_path = Path(st.sidebar.text_input("Modelo", str(DEFAULT_MODEL_PATH)))

    confidence_threshold = st.sidebar.slider("Confianza minima", 0.40, 0.95, 0.75, 0.05)
    stable_frames = st.sidebar.slider("Frames estables", 3, 18, 8, 1)
    mirror_camera = st.sidebar.toggle("Espejar camara", value=True)

    st.title("Traductor LSC")

    if not model_path.exists():
        st.markdown('<span class="status-warn">Entrenamiento pendiente</span>', unsafe_allow_html=True)
        render_setup_message()
        return

    predictor = load_predictor(str(model_path))
    model_detail = predictor.model_type
    if predictor.model_type == "sequence":
        model_detail = f"sequence/{predictor.sequence_length or 6} frames"
    st.markdown(
        f'<span class="status-ok">Modelo activo:</span> {predictor.model_name} ({model_detail})',
        unsafe_allow_html=True,
    )

    tab_live, tab_snapshot, tab_metrics = st.tabs(["Camara", "Imagen", "Metricas"])

    with tab_live:
        if not WEBRTC_AVAILABLE:
            st.error("Falta streamlit-webrtc. Instala dependencias con: pip install -r requirements.txt")
        else:
            left, right = st.columns([0.72, 0.28], gap="large")
            with left:
                processor_factory = lambda: LSCVideoProcessor(
                    str(model_path),
                    confidence_threshold,
                    stable_frames,
                    mirror_camera,
                )
                ctx = webrtc_streamer(
                    key=f"lsc-live-{confidence_threshold}-{stable_frames}-{mirror_camera}",
                    mode=WebRtcMode.SENDRECV,
                    rtc_configuration=RTCConfiguration(
                        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
                    ),
                    video_processor_factory=processor_factory,
                    media_stream_constraints={"video": True, "audio": False},
                    async_processing=True,
                )

            with right:
                label_slot = st.empty()
                confidence_slot = st.empty()
                text_slot = st.empty()

                col_a, col_b, col_c = st.columns(3)
                if col_a.button("Espacio", use_container_width=True) and ctx.video_processor:
                    ctx.video_processor.space()
                if col_b.button("Borrar", use_container_width=True) and ctx.video_processor:
                    ctx.video_processor.delete()
                if col_c.button("Limpiar", use_container_width=True) and ctx.video_processor:
                    ctx.video_processor.clear()

                while ctx.state.playing and ctx.video_processor:
                    with ctx.video_processor.lock:
                        label = ctx.video_processor.latest_label or "-"
                        confidence = ctx.video_processor.latest_confidence
                        text = ctx.video_processor.latest_text or ""
                    label_slot.markdown(
                        f'<div class="metric-card"><div class="label">Letra</div><div class="value">{label}</div></div>',
                        unsafe_allow_html=True,
                    )
                    confidence_slot.markdown(
                        f'<div class="metric-card"><div class="label">Confianza</div><div class="value">{confidence:.0%}</div></div>',
                        unsafe_allow_html=True,
                    )
                    safe_text = text if text else "-"
                    text_slot.markdown(
                        f'<div class="metric-card"><div class="label">Texto</div><div class="value">{safe_text}</div></div>',
                        unsafe_allow_html=True,
                    )
                    time.sleep(0.2)

    with tab_snapshot:
        snapshot = st.camera_input("Captura una imagen")
        uploaded = st.file_uploader("O carga una imagen", type=["jpg", "jpeg", "png", "webp"])
        image_input = snapshot or uploaded
        if image_input is not None:
            process_snapshot(predictor, image_input)

    with tab_metrics:
        metrics = predictor.metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric("Accuracy", f"{metrics.get('accuracy', 0):.1%}")
        with col2:
            render_metric("F1 macro", f"{metrics.get('f1_macro', 0):.1%}")
        with col3:
            render_metric("Clases", str(len(predictor.labels)))
        st.json(metrics)


if __name__ == "__main__":
    main()
