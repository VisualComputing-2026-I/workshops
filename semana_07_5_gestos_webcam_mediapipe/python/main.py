"""
Taller: Visión por Computadora con MediaPipe Hands
===================================================
Objetivos:
  1. Capturar video en tiempo real desde webcam.
  2. Detectar manos con MediaPipe Hands.
  3. Medir dedos extendidos y distancia índice-pulgar.
  4. Acciones visuales: cambiar fondo, mover objeto, cambiar escena.

Controles:
  - Q  ->  Salir
"""

import cv2
import mediapipe as mp
import numpy as np
import math

# ─────────────────────────────────────────────
#  CONFIGURACIÓN RÁPIDA
# ─────────────────────────────────────────────
CAM_INDEX = 0          # Cambia a 1 o 2 si la USB externa no aparece
WIDTH, HEIGHT = 1280, 720

# ─────────────────────────────────────────────
#  INICIALIZACIÓN MEDIAPIPE
# ─────────────────────────────────────────────
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
mp_style = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6,
)


# ─────────────────────────────────────────────
#  UTILIDADES
# ─────────────────────────────────────────────

def contar_dedos(landmarks, handedness: str) -> int:
    """
    Cuenta dedos extendidos.
    Usa la punta vs. la articulación media de cada dedo.
    El pulgar compara coordenadas X (invertido según mano).
    """
    tips    = [4, 8, 12, 16, 20]   # índices de punta de cada dedo
    pip     = [3, 6, 10, 14, 18]   # articulación media

    dedos_abiertos = 0

    # Pulgar: compara X relativo a si es mano izquierda o derecha
    if handedness == "Right":
        if landmarks[tips[0]].x < landmarks[pip[0]].x:
            dedos_abiertos += 1
    else:
        if landmarks[tips[0]].x > landmarks[pip[0]].x:
            dedos_abiertos += 1

    # Resto de dedos: punta más arriba (Y menor) que articulación
    for i in range(1, 5):
        if landmarks[tips[i]].y < landmarks[pip[i]].y:
            dedos_abiertos += 1

    return dedos_abiertos


def distancia_indice_pulgar(landmarks, w: int, h: int) -> float:
    """Distancia en píxeles entre punta del pulgar (4) e índice (8)."""
    x1 = int(landmarks[4].x * w);  y1 = int(landmarks[4].y * h)
    x2 = int(landmarks[8].x * w);  y2 = int(landmarks[8].y * h)
    return math.hypot(x2 - x1, y2 - y1)


def punto_px(landmark, w: int, h: int):
    """Convierte landmark normalizado a coordenadas de píxel."""
    return int(landmark.x * w), int(landmark.y * h)


# ─────────────────────────────────────────────
#  ESTADO GLOBAL DE LA APLICACIÓN
# ─────────────────────────────────────────────

ESCENAS = ["gestos", "pintura", "objeto"]   # ciclo de escenas

estado = {
    "escena": 0,                  # índice de escena actual
    "fondo_idx": 0,               # índice de color de fondo
    "objeto_pos": [WIDTH // 2, HEIGHT // 2],   # posición del objeto móvil
    "canvas": None,               # lienzo de pintura (se crea en el loop)
    "ultimo_cambio_escena": 0,    # frame en que se cambió de escena
    "cooldown_frames": 40,        # frames de espera entre cambios de escena
    "frame_num": 0,
}

COLORES_FONDO = [
    (20,  20,  20),    # negro suave
    (180, 60,  60),    # rojo
    (60,  130, 60),    # verde
    (50,  80,  180),   # azul
    (130, 60,  130),   # morado
    (200, 130, 30),    # naranja
]


# ─────────────────────────────────────────────
#  ESCENA 0 – GESTOS (métricas en pantalla)
# ─────────────────────────────────────────────

def escena_gestos(frame, landmarks, n_dedos, dist, handedness):
    h, w = frame.shape[:2]

    # Fondo dinámico según número de dedos
    color_fondo = COLORES_FONDO[n_dedos % len(COLORES_FONDO)]
    overlay = np.full_like(frame, color_fondo, dtype=np.uint8)
    cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

    # Dibujar landmarks
    mp_draw.draw_landmarks(
        frame,
        landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_style.get_default_hand_landmarks_style(),
        mp_style.get_default_hand_connections_style(),
    )

    # Línea y círculo entre pulgar e índice
    p4 = punto_px(landmarks.landmark[4],  w, h)
    p8 = punto_px(landmarks.landmark[8],  w, h)
    cv2.line(frame, p4, p8, (255, 230, 0), 2)
    mid = ((p4[0]+p8[0])//2, (p4[1]+p8[1])//2)
    cv2.circle(frame, mid, 6, (255, 230, 0), -1)

    # HUD
    cv2.putText(frame, f"Dedos: {n_dedos}",   (30, 50),  cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255,255,255), 2)
    cv2.putText(frame, f"Dist:  {dist:.0f}px", (30, 95),  cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255,255,255), 2)
    cv2.putText(frame, f"Mano:  {handedness}", (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255,255,255), 2)


# ─────────────────────────────────────────────
#  ESCENA 1 – PINTURA (trazar con el índice)
# ─────────────────────────────────────────────

COLORES_PINCEL = [(0,0,255),(0,200,0),(255,100,0),(180,0,180),(0,200,200)]

def escena_pintura(frame, landmarks, n_dedos, estado):
    h, w = frame.shape[:2]

    if estado["canvas"] is None or estado["canvas"].shape[:2] != (h, w):
        estado["canvas"] = np.zeros((h, w, 3), dtype=np.uint8)

    canvas = estado["canvas"]

    p8 = punto_px(landmarks.landmark[8], w, h)   # punta índice

    color_pincel = COLORES_PINCEL[n_dedos % len(COLORES_PINCEL)]

    if n_dedos == 0:
        # Puño cerrado -> borrar canvas
        estado["canvas"] = np.zeros((h, w, 3), dtype=np.uint8)
    elif n_dedos == 1:
        # Solo índice -> dibujar
        cv2.circle(canvas, p8, 10, color_pincel, -1)
    # 2+ dedos -> solo ver (no borra, no dibuja)

    # Fusionar canvas con frame
    mask = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
    frame[mask > 0] = canvas[mask > 0]

    # Dibujar punta del índice
    cv2.circle(frame, p8, 12, color_pincel, 3)

    # HUD
    cv2.putText(frame, "PINTURA", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_pincel, 3)
    cv2.putText(frame, "1 dedo=dibujar  |  Puno=borrar", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200,200,200), 1)


# ─────────────────────────────────────────────
#  ESCENA 2 – OBJETO MÓVIL
# ─────────────────────────────────────────────

def escena_objeto(frame, landmarks, n_dedos, dist, estado):
    h, w = frame.shape[:2]

    # Fondo con gradiente suave
    fondo = np.zeros_like(frame)
    for i in range(h):
        t = i / h
        fondo[i, :] = (int(15 + 25*t), int(10 + 40*t), int(40 + 60*t))
    cv2.addWeighted(fondo, 0.5, frame, 0.5, 0, frame)

    # El centro de la mano (muñeca = landmark 0) guía el objeto
    cx = int(landmarks.landmark[0].x * w)
    cy = int(landmarks.landmark[0].y * h)

    # Interpolación suave (lerp)
    ox, oy = estado["objeto_pos"]
    estado["objeto_pos"][0] = int(ox * 0.8 + cx * 0.2)
    estado["objeto_pos"][1] = int(oy * 0.8 + cy * 0.2)
    ox, oy = estado["objeto_pos"]

    # Tamaño del objeto varía con la distancia índice-pulgar
    radio = int(np.clip(dist * 0.4, 20, 120))

    # Forma según dedos
    color_obj = COLORES_FONDO[(n_dedos + 2) % len(COLORES_FONDO)]
    if n_dedos <= 2:
        # Círculo
        cv2.circle(frame, (ox, oy), radio, color_obj, -1)
        cv2.circle(frame, (ox, oy), radio, (255,255,255), 2)
    else:
        # Rectángulo
        lado = radio
        cv2.rectangle(frame, (ox-lado, oy-lado), (ox+lado, oy+lado), color_obj, -1)
        cv2.rectangle(frame, (ox-lado, oy-lado), (ox+lado, oy+lado), (255,255,255), 2)

    # Landmarks encima
    mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    # HUD
    cv2.putText(frame, "OBJETO",  (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)
    cv2.putText(frame, f"Radio: {radio}px  |  Dedos: {n_dedos}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 1)


# ─────────────────────────────────────────────
#  DETECCIÓN DE GESTO "PALMA ABIERTA" -> cambiar escena
# ─────────────────────────────────────────────

def detectar_cambio_escena(n_dedos, estado) -> bool:
    """Activa cambio de escena si se muestran 5 dedos y pasó el cooldown."""
    frames_desde_cambio = estado["frame_num"] - estado["ultimo_cambio_escena"]
    if n_dedos == 5 and frames_desde_cambio > estado["cooldown_frames"]:
        estado["escena"] = (estado["escena"] + 1) % len(ESCENAS)
        estado["ultimo_cambio_escena"] = estado["frame_num"]
        return True
    return False


# ─────────────────────────────────────────────
#  OVERLAY DE AYUDA (esquina inferior)
# ─────────────────────────────────────────────

NOMBRES_ESCENAS = {
    0: "Escena 1: GESTOS",
    1: "Escena 2: PINTURA",
    2: "Escena 3: OBJETO",
}

def dibujar_hud_global(frame, escena_idx, cambio_activo):
    h, w = frame.shape[:2]
    # Nombre de escena actual
    texto_escena = NOMBRES_ESCENAS[escena_idx]
    cv2.putText(frame, texto_escena, (30, h - 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (240, 200, 80), 2)

    # Instrucción cambio de escena
    cv2.putText(frame, "[Palma abierta = cambiar escena]  [Q = salir]",
                (30, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)

    # Flash al cambiar
    if cambio_activo:
        overlay = np.ones_like(frame, dtype=np.uint8) * 255
        cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)


# ─────────────────────────────────────────────
#  LOOP PRINCIPAL
# ─────────────────────────────────────────────

def main():
    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    if not cap.isOpened():
        print(f"[ERROR] No se pudo abrir la cámara con índice {CAM_INDEX}.")
        print("        Prueba cambiando CAM_INDEX a 1 o 2 en el script.")
        return

    print("✅ Cámara abierta. Mostrando ventana... (presiona Q para salir)")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("[ERROR] No se pudo leer el frame.")
            break

        estado["frame_num"] += 1
        frame = cv2.flip(frame, 1)          # espejo natural
        h, w  = frame.shape[:2]

        # ── Procesamiento MediaPipe ──────────────────────
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultado = hands.process(rgb)

        cambio_escena_activo = False

        if resultado.multi_hand_landmarks and resultado.multi_handedness:
            lm        = resultado.multi_hand_landmarks[0]
            hand_info = resultado.multi_handedness[0].classification[0]
            handedness = hand_info.label          # "Left" o "Right"

            n_dedos = contar_dedos(lm.landmark, handedness)
            dist    = distancia_indice_pulgar(lm.landmark, w, h)

            # Verificar gesto de cambio de escena
            cambio_escena_activo = detectar_cambio_escena(n_dedos, estado)

            # Despachar a la escena activa
            escena_actual = ESCENAS[estado["escena"]]

            if escena_actual == "gestos":
                escena_gestos(frame, lm, n_dedos, dist, handedness)

            elif escena_actual == "pintura":
                escena_pintura(frame, lm, n_dedos, estado)

            elif escena_actual == "objeto":
                escena_objeto(frame, lm, n_dedos, dist, estado)

        else:
            # Sin mano detectada: fondo neutro + mensaje
            overlay = np.full_like(frame, (25, 25, 35), dtype=np.uint8)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
            cv2.putText(frame, "Muestra tu mano a la camara...",
                        (30, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (180, 180, 180), 2)

        # HUD global (siempre visible)
        dibujar_hud_global(frame, estado["escena"], cambio_escena_activo)

        cv2.imshow("Taller MediaPipe Hands", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("👋 Sesión finalizada.")


if __name__ == "__main__":
    main()