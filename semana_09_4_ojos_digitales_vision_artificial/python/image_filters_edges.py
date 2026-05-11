from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np


FILTER_NAMES = {
    0: "Gris",
    1: "Blur",
    2: "Sharpening",
    3: "Sobel",
    4: "Laplaciano",
}


def ensure_odd(value: int, minimum: int = 1, maximum: int = 31) -> int:
    value = max(minimum, min(maximum, int(value)))
    if value % 2 == 0:
        value += 1
    return min(value, maximum if maximum % 2 == 1 else maximum - 1)


def create_demo_image(width: int = 900, height: int = 600) -> np.ndarray:
    """Create a synthetic BGR image so the project runs without external files."""
    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[:] = (32, 40, 48)

    for x in range(width):
        blue = 40 + int(80 * x / width)
        green = 70 + int(90 * (1 - x / width))
        image[:, x] = (blue, green, 95)

    cv2.rectangle(image, (70, 80), (360, 300), (40, 180, 230), -1)
    cv2.rectangle(image, (70, 80), (360, 300), (255, 255, 255), 4)
    cv2.circle(image, (620, 190), 115, (210, 70, 80), -1)
    cv2.circle(image, (620, 190), 115, (245, 245, 245), 4)
    cv2.line(image, (120, 460), (780, 390), (255, 255, 255), 8)
    cv2.line(image, (120, 505), (780, 505), (60, 220, 120), 10)
    cv2.putText(
        image,
        "Demo OpenCV",
        (95, 390),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.4,
        (245, 245, 245),
        3,
        cv2.LINE_AA,
    )

    rng = np.random.default_rng(7)
    noise = rng.normal(0, 8, image.shape).astype(np.int16)
    return np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)


def load_color_image(image_path: str | None) -> np.ndarray:
    if image_path is None:
        return create_demo_image()

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe la imagen: {path}")

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"No se pudo cargar la imagen como archivo de imagen: {path}")
    return image


def to_gray(image_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)


def blur_convolution(image_bgr: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    kernel_size = ensure_odd(kernel_size)
    kernel = np.ones((kernel_size, kernel_size), dtype=np.float32)
    kernel /= float(kernel_size * kernel_size)
    return cv2.filter2D(image_bgr, ddepth=-1, kernel=kernel)


def sharpen_convolution(image_bgr: np.ndarray) -> np.ndarray:
    kernel = np.array(
        [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0],
        ],
        dtype=np.float32,
    )
    return cv2.filter2D(image_bgr, ddepth=-1, kernel=kernel)


def sobel_edges(gray: np.ndarray, kernel_size: int = 3) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    kernel_size = ensure_odd(kernel_size, minimum=1, maximum=7)
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=kernel_size)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=kernel_size)

    abs_x = cv2.convertScaleAbs(sobel_x)
    abs_y = cv2.convertScaleAbs(sobel_y)
    magnitude = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
    return abs_x, abs_y, magnitude


def laplacian_edges(gray: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    kernel_size = ensure_odd(kernel_size, minimum=1, maximum=31)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=kernel_size)
    return cv2.convertScaleAbs(laplacian)


def compute_results(
    image_bgr: np.ndarray,
    blur_kernel: int = 5,
    edge_kernel: int = 3,
) -> dict[str, np.ndarray]:
    gray = to_gray(image_bgr)
    sobel_x, sobel_y, sobel_magnitude = sobel_edges(gray, edge_kernel)

    return {
        "Original": cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB),
        "Escala de grises": gray,
        "Blur": cv2.cvtColor(blur_convolution(image_bgr, blur_kernel), cv2.COLOR_BGR2RGB),
        "Sharpening": cv2.cvtColor(sharpen_convolution(image_bgr), cv2.COLOR_BGR2RGB),
        "Sobel X": sobel_x,
        "Sobel Y": sobel_y,
        "Sobel X + Y": sobel_magnitude,
        "Laplaciano": laplacian_edges(gray, edge_kernel),
    }


def show_with_matplotlib(results: dict[str, np.ndarray]) -> None:
    figure, axes = plt.subplots(2, 4, figsize=(15, 8))
    figure.suptitle("Comparacion de filtros y detectores de bordes", fontsize=14)

    for axis, (title, image) in zip(axes.ravel(), results.items()):
        cmap = "gray" if image.ndim == 2 else None
        axis.imshow(image, cmap=cmap)
        axis.set_title(title)
        axis.axis("off")

    plt.tight_layout()
    plt.show()


def show_with_cv2(results: dict[str, np.ndarray]) -> None:
    for title, image in results.items():
        if image.ndim == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imshow(title, image)

    print("Presiona cualquier tecla en una ventana de OpenCV para cerrar.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def apply_selected_filter(image_bgr: np.ndarray, filter_id: int, kernel_size: int) -> np.ndarray:
    filter_id = int(filter_id)
    kernel_size = ensure_odd(kernel_size)
    gray = to_gray(image_bgr)

    if filter_id == 0:
        return gray
    if filter_id == 1:
        return blur_convolution(image_bgr, kernel_size)
    if filter_id == 2:
        return sharpen_convolution(image_bgr)
    if filter_id == 3:
        _, _, magnitude = sobel_edges(gray, kernel_size)
        return magnitude
    if filter_id == 4:
        return laplacian_edges(gray, kernel_size)

    return gray


def add_status_text(image: np.ndarray, text: str) -> np.ndarray:
    if image.ndim == 2:
        canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        canvas = image.copy()

    cv2.rectangle(canvas, (0, 0), (canvas.shape[1], 42), (0, 0, 0), -1)
    cv2.putText(
        canvas,
        text,
        (12, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return canvas


def run_interactive_image(image_bgr: np.ndarray) -> None:
    window_name = "Sliders - filtros OpenCV"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.createTrackbar("Filtro 0-4", window_name, 0, 4, lambda _value: None)
    cv2.createTrackbar("Kernel", window_name, 5, 31, lambda _value: None)

    while True:
        filter_id = cv2.getTrackbarPos("Filtro 0-4", window_name)
        kernel_size = ensure_odd(cv2.getTrackbarPos("Kernel", window_name))
        result = apply_selected_filter(image_bgr, filter_id, kernel_size)
        label = f"{FILTER_NAMES.get(filter_id, 'Filtro')} | kernel={kernel_size} | q/Esc para salir"
        cv2.imshow(window_name, add_status_text(result, label))

        key = cv2.waitKey(30) & 0xFF
        if key in (27, ord("q")):
            break

    cv2.destroyAllWindows()


def run_webcam(camera_index: int = 0) -> None:
    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise RuntimeError(f"No se pudo abrir la webcam con indice {camera_index}")

    window_name = "Webcam - filtros OpenCV"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.createTrackbar("Filtro 0-4", window_name, 0, 4, lambda _value: None)
    cv2.createTrackbar("Kernel", window_name, 5, 31, lambda _value: None)

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("No se pudo leer un frame de la webcam")

            filter_id = cv2.getTrackbarPos("Filtro 0-4", window_name)
            kernel_size = ensure_odd(cv2.getTrackbarPos("Kernel", window_name))
            result = apply_selected_filter(frame, filter_id, kernel_size)
            label = f"{FILTER_NAMES.get(filter_id, 'Filtro')} | kernel={kernel_size} | q/Esc para salir"
            cv2.imshow(window_name, add_status_text(result, label))

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


def prompt_choice(title: str, choices: dict[str, str]) -> str:
    while True:
        print(f"\n{title}")
        for key, label in choices.items():
            print(f"{key}. {label}")

        selected = input("Selecciona una opcion: ").strip()
        if selected in choices:
            return selected

        print("Opcion no valida. Intenta de nuevo.")


def prompt_int(message: str, default: int, minimum: int | None = None, maximum: int | None = None) -> int:
    while True:
        raw_value = input(f"{message} [{default}]: ").strip()
        if not raw_value:
            return default

        try:
            value = int(raw_value)
        except ValueError:
            print("Ingresa un numero entero.")
            continue

        if minimum is not None and value < minimum:
            print(f"El valor minimo es {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"El valor maximo es {maximum}.")
            continue

        return value


def prompt_image_path() -> str:
    while True:
        image_path = input("Ruta de la imagen: ").strip().strip('"')
        if Path(image_path).exists():
            return image_path
        print("No existe un archivo en esa ruta. Intenta de nuevo.")


def prompt_image_source() -> np.ndarray:
    source = prompt_choice(
        "Fuente de imagen",
        {
            "1": "Usar imagen demo generada por el programa",
            "2": "Cargar imagen propia desde una ruta",
        },
    )

    if source == "1":
        return load_color_image(None)

    return load_color_image(prompt_image_path())


def prompt_display_method() -> str:
    selected = prompt_choice(
        "Metodo de visualizacion",
        {
            "1": "Matplotlib",
            "2": "Ventanas de OpenCV",
        },
    )
    return "matplotlib" if selected == "1" else "cv2"


def run_static_comparison_from_menu() -> None:
    image_bgr = prompt_image_source()
    display = prompt_display_method()
    blur_kernel = ensure_odd(prompt_int("Tamano de kernel para blur", default=5, minimum=1, maximum=31))
    edge_kernel = ensure_odd(prompt_int("Tamano de kernel para Sobel/Laplaciano", default=3, minimum=1, maximum=31))

    results = compute_results(image_bgr, blur_kernel=blur_kernel, edge_kernel=edge_kernel)
    if display == "cv2":
        show_with_cv2(results)
    else:
        show_with_matplotlib(results)


def run_interactive_image_from_menu() -> None:
    image_bgr = prompt_image_source()
    run_interactive_image(image_bgr)


def run_webcam_from_menu() -> None:
    camera_index = prompt_int("Indice de camara", default=0, minimum=0)
    run_webcam(camera_index)


def run_menu() -> None:
    while True:
        selected = prompt_choice(
            "Menu principal - Procesamiento de imagenes con OpenCV",
            {
                "1": "Comparacion visual de filtros y bordes",
                "2": "Sliders interactivos con una imagen",
                "3": "Webcam en tiempo real con sliders",
                "4": "Salir",
            },
        )

        try:
            if selected == "1":
                run_static_comparison_from_menu()
            elif selected == "2":
                run_interactive_image_from_menu()
            elif selected == "3":
                run_webcam_from_menu()
            elif selected == "4":
                print("Programa finalizado.")
                return
        except (FileNotFoundError, RuntimeError, ValueError) as error:
            print(f"Error: {error}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filtros convolucionales y deteccion de bordes con OpenCV."
    )
    parser.add_argument("--image", help="Ruta de la imagen a color. Si se omite, se usa una demo.")
    parser.add_argument(
        "--display",
        choices=("matplotlib", "cv2"),
        default="matplotlib",
        help="Metodo de visualizacion para la comparacion estatica.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Abre sliders con cv2.createTrackbar para procesar una imagen.",
    )
    parser.add_argument(
        "--webcam",
        action="store_true",
        help="Activa procesamiento en tiempo real usando webcam.",
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Indice de camara para --webcam.",
    )
    parser.add_argument(
        "--blur-kernel",
        type=int,
        default=5,
        help="Tamano de kernel para blur en la comparacion estatica.",
    )
    parser.add_argument(
        "--edge-kernel",
        type=int,
        default=3,
        help="Tamano de kernel para Sobel y Laplaciano en la comparacion estatica.",
    )
    return parser.parse_args()


def main() -> None:
    if len(sys.argv) == 1:
        run_menu()
        return

    args = parse_args()

    if args.webcam:
        run_webcam(args.camera_index)
        return

    image_bgr = load_color_image(args.image)

    if args.interactive:
        run_interactive_image(image_bgr)
        return

    results = compute_results(
        image_bgr,
        blur_kernel=args.blur_kernel,
        edge_kernel=args.edge_kernel,
    )

    if args.display == "cv2":
        show_with_cv2(results)
    else:
        show_with_matplotlib(results)


if __name__ == "__main__":
    main()
