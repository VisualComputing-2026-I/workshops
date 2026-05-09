"""
Taller: Segmentación de Imágenes con OpenCV
Técnicas: Umbralización y Detección de Formas Simples
Herramientas: opencv-python, numpy, matplotlib
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
import urllib.request
import os


# ─────────────────────────────────────────────
# 1. CARGA DE IMAGEN
# ─────────────────────────────────────────────

def cargar_imagen(ruta=None):
    """
    Carga una imagen en escala de grises.
    Si no se proporciona ruta, descarga una imagen de muestra.
    """
    if ruta is None:
        # Imagen de muestra con formas geométricas (generada con numpy)
        print("[INFO] No se proporcionó imagen. Generando imagen de prueba con formas...")
        img_color = np.ones((400, 600, 3), dtype=np.uint8) * 240  # Fondo gris claro

        # Dibujar formas
        cv2.circle(img_color, (100, 100), 60, (30, 30, 30), -1)
        cv2.rectangle(img_color, (200, 50), (350, 160), (50, 50, 50), -1)
        cv2.ellipse(img_color, (480, 100), (80, 45), 30, 0, 360, (20, 20, 20), -1)
        cv2.circle(img_color, (80, 280), 40, (60, 60, 60), -1)
        cv2.rectangle(img_color, (180, 240), (290, 330), (40, 40, 40), -1)
        cv2.ellipse(img_color, (400, 290), (100, 55), 0, 0, 360, (25, 25, 25), -1)
        cv2.circle(img_color, (530, 300), 50, (35, 35, 35), -1)

        imagen_gris = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        imagen_color = img_color
    else:
        imagen_color = cv2.imread(ruta)
        if imagen_color is None:
            print(f"[ERROR] No se pudo cargar la imagen desde: {ruta}")
            sys.exit(1)
        imagen_gris = cv2.cvtColor(imagen_color, cv2.COLOR_BGR2GRAY)

    print(f"[INFO] Imagen cargada — Tamaño: {imagen_gris.shape[1]}x{imagen_gris.shape[0]} px")
    return imagen_gris, imagen_color


# ─────────────────────────────────────────────
# 2. SEGMENTACIÓN BINARIA
# ─────────────────────────────────────────────

def aplicar_umbral_fijo(imagen_gris, valor_umbral=127):
    """Umbral fijo con cv2.threshold (método OTSU + valor fijo)."""
    # Umbral fijo manual
    _, binaria_fija = cv2.threshold(
        imagen_gris, valor_umbral, 255, cv2.THRESH_BINARY_INV
    )
    # Umbral automático OTSU (bonus)
    valor_otsu, binaria_otsu = cv2.threshold(
        imagen_gris, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    print(f"[INFO] Umbral fijo aplicado: {valor_umbral} | Umbral OTSU calculado: {valor_otsu:.1f}")
    return binaria_fija, binaria_otsu, valor_otsu


def aplicar_umbral_adaptativo(imagen_gris):
    """Umbral adaptativo con cv2.adaptiveThreshold (media y gaussiano)."""
    binaria_media = cv2.adaptiveThreshold(
        imagen_gris, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=11, C=2
    )
    binaria_gaussiana = cv2.adaptiveThreshold(
        imagen_gris, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=11, C=2
    )
    print("[INFO] Umbral adaptativo aplicado (Media y Gaussiano).")
    return binaria_media, binaria_gaussiana


# ─────────────────────────────────────────────
# 3. LIMPIEZA MORFOLÓGICA (opcional pero recomendada)
# ─────────────────────────────────────────────

def limpiar_imagen(binaria):
    """Elimina ruido con operaciones morfológicas."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    limpia = cv2.morphologyEx(binaria, cv2.MORPH_CLOSE, kernel)
    limpia = cv2.morphologyEx(limpia, cv2.MORPH_OPEN, kernel)
    return limpia


# ─────────────────────────────────────────────
# 4. DETECCIÓN DE CONTORNOS
# ─────────────────────────────────────────────

def detectar_contornos(binaria, area_minima=500):
    """
    Detecta contornos con cv2.findContours().
    Filtra contornos pequeños por área mínima.
    """
    contornos, jerarquia = cv2.findContours(
        binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    # Filtrar por área mínima para eliminar ruido
    contornos_filtrados = [c for c in contornos if cv2.contourArea(c) >= area_minima]
    print(f"[INFO] Contornos totales detectados: {len(contornos)} | "
          f"Después de filtrar (área ≥ {area_minima} px²): {len(contornos_filtrados)}")
    return contornos_filtrados


# ─────────────────────────────────────────────
# 5. DIBUJAR CONTORNOS, CENTROS Y BOUNDING BOXES
# ─────────────────────────────────────────────

def dibujar_resultados(imagen_color, contornos):
    """
    Dibuja sobre la imagen:
    - Contornos (verde)
    - Centro de masa / centroide (rojo)
    - Bounding box (azul)
    - Número de forma (amarillo)
    """
    resultado = imagen_color.copy()
    if len(resultado.shape) == 2:  # Si es escala de grises, convertir
        resultado = cv2.cvtColor(resultado, cv2.COLOR_GRAY2BGR)

    datos_formas = []

    for i, contorno in enumerate(contornos, start=1):
        # — Contorno —
        cv2.drawContours(resultado, [contorno], -1, (0, 220, 0), 2)

        # — Centro de masa (Momentos) —
        M = cv2.moments(contorno)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            x, y, w, h = cv2.boundingRect(contorno)
            cx, cy = x + w // 2, y + h // 2

        cv2.circle(resultado, (cx, cy), 5, (0, 0, 255), -1)

        # — Bounding Box —
        x, y, w, h = cv2.boundingRect(contorno)
        cv2.rectangle(resultado, (x, y), (x + w, y + h), (255, 100, 0), 2)

        # — Etiqueta de número —
        cv2.putText(resultado, str(i), (cx - 8, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # — Guardar datos —
        area = cv2.contourArea(contorno)
        perimetro = cv2.arcLength(contorno, True)
        datos_formas.append({
            "id": i,
            "centroide": (cx, cy),
            "bounding_box": (x, y, w, h),
            "area": area,
            "perimetro": perimetro
        })

    return resultado, datos_formas


# ─────────────────────────────────────────────
# 6. MÉTRICAS
# ─────────────────────────────────────────────

def calcular_metricas(datos_formas):
    """Calcula y muestra métricas básicas de las formas detectadas."""
    n = len(datos_formas)
    if n == 0:
        print("[AVISO] No se detectaron formas.")
        return

    areas = [d["area"] for d in datos_formas]
    perimetros = [d["perimetro"] for d in datos_formas]

    print("\n" + "═" * 50)
    print("  MÉTRICAS DE SEGMENTACIÓN")
    print("═" * 50)
    print(f"  Número de formas detectadas : {n}")
    print(f"  Área promedio               : {np.mean(areas):.1f} px²")
    print(f"  Área máxima                 : {np.max(areas):.1f} px²")
    print(f"  Área mínima                 : {np.min(areas):.1f} px²")
    print(f"  Perímetro promedio          : {np.mean(perimetros):.1f} px")
    print("─" * 50)
    print(f"  {'ID':>4}  {'Área (px²)':>12}  {'Perímetro (px)':>15}  {'Centroide':>18}")
    print("─" * 50)
    for d in datos_formas:
        print(f"  {d['id']:>4}  {d['area']:>12.1f}  {d['perimetro']:>15.1f}  "
              f"  ({d['centroide'][0]:>4}, {d['centroide'][1]:>4})")
    print("═" * 50 + "\n")

    return {"n": n, "area_promedio": np.mean(areas), "perimetro_promedio": np.mean(perimetros)}


# ─────────────────────────────────────────────
# 7. VISUALIZACIÓN COMPLETA
# ─────────────────────────────────────────────

def visualizar_resultados(imagen_gris, imagen_color, binaria_fija, binaria_otsu,
                           binaria_adaptativa, imagen_resultado, datos_formas, metricas):
    """Muestra todas las etapas del pipeline en una figura organizada."""

    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#1a1a2e')
    titulo_style = dict(color='white', fontsize=11, fontweight='bold', pad=8)
    cmap_bin = 'gray'

    axes = []
    posiciones = [(2, 4, i) for i in range(1, 9)]
    for pos in posiciones:
        ax = fig.add_subplot(*pos)
        ax.set_facecolor('#16213e')
        for spine in ax.spines.values():
            spine.set_edgecolor('#0f3460')
        ax.tick_params(colors='#aaaaaa', labelsize=7)
        axes.append(ax)

    # — Panel 1: Original en escala de grises —
    axes[0].imshow(imagen_gris, cmap='gray')
    axes[0].set_title("1. Imagen Original\n(Escala de grises)", **titulo_style)

    # — Panel 2: Umbral fijo —
    axes[1].imshow(binaria_fija, cmap=cmap_bin)
    axes[1].set_title("2. Umbral Fijo\n(cv2.THRESH_BINARY_INV, T=127)", **titulo_style)

    # — Panel 3: Umbral OTSU —
    axes[2].imshow(binaria_otsu, cmap=cmap_bin)
    axes[2].set_title(f"3. Umbral OTSU\n(T automático = {metricas.get('otsu', '?')})",
                      **titulo_style)

    # — Panel 4: Umbral adaptativo gaussiano —
    axes[3].imshow(binaria_adaptativa, cmap=cmap_bin)
    axes[3].set_title("4. Umbral Adaptativo\n(Gaussiano, blk=11)", **titulo_style)

    # — Panel 5: Imagen procesada con contornos —
    img_show = cv2.cvtColor(imagen_resultado, cv2.COLOR_BGR2RGB)
    axes[4].imshow(img_show)
    axes[4].set_title("5. Contornos + BBox + Centroides\n(sobre imagen original)", **titulo_style)

    # — Panel 6: Histograma de áreas —
    areas = [d["area"] for d in datos_formas]
    axes[5].bar(range(1, len(areas) + 1), areas, color='#e94560', edgecolor='#0f3460')
    axes[5].set_title("6. Área por Forma (px²)", **titulo_style)
    axes[5].set_xlabel("ID Forma", color='#aaaaaa', fontsize=8)
    axes[5].set_ylabel("Área (px²)", color='#aaaaaa', fontsize=8)
    axes[5].axhline(np.mean(areas), color='yellow', linestyle='--', linewidth=1.2,
                    label=f'Promedio: {np.mean(areas):.0f}')
    axes[5].legend(fontsize=8, facecolor='#16213e', labelcolor='white')

    # — Panel 7: Histograma de perímetros —
    perimetros = [d["perimetro"] for d in datos_formas]
    axes[6].bar(range(1, len(perimetros) + 1), perimetros, color='#0f3460', edgecolor='#e94560')
    axes[6].set_title("7. Perímetro por Forma (px)", **titulo_style)
    axes[6].set_xlabel("ID Forma", color='#aaaaaa', fontsize=8)
    axes[6].set_ylabel("Perímetro (px)", color='#aaaaaa', fontsize=8)
    axes[6].axhline(np.mean(perimetros), color='cyan', linestyle='--', linewidth=1.2,
                    label=f'Promedio: {np.mean(perimetros):.0f}')
    axes[6].legend(fontsize=8, facecolor='#16213e', labelcolor='white')

    # — Panel 8: Tabla de métricas —
    axes[7].axis('off')
    tabla_data = [
        ["Formas detectadas", str(metricas['n'])],
        ["Área promedio", f"{metricas['area_promedio']:.1f} px²"],
        ["Perímetro promedio", f"{metricas['perimetro_promedio']:.1f} px"],
    ]
    tabla = axes[7].table(
        cellText=tabla_data,
        colLabels=["Métrica", "Valor"],
        cellLoc='center', loc='center',
        bbox=[0.05, 0.2, 0.9, 0.6]
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    for (row, col), cell in tabla.get_celld().items():
        cell.set_facecolor('#0f3460' if row == 0 else '#16213e')
        cell.set_text_props(color='white')
        cell.set_edgecolor('#e94560')
    axes[7].set_title("8. Resumen de Métricas", **titulo_style)

    # — Leyenda general —
    leyenda = [
        mpatches.Patch(color='#00dc00', label='Contorno (verde)'),
        mpatches.Patch(color='red', label='Centroide (rojo)'),
        mpatches.Patch(color='#6464ff', label='Bounding Box (azul)'),
    ]
    fig.legend(handles=leyenda, loc='lower center', ncol=3,
               facecolor='#1a1a2e', edgecolor='#0f3460',
               labelcolor='white', fontsize=9, bbox_to_anchor=(0.5, 0.01))

    plt.suptitle("Taller: Segmentación de Imágenes con OpenCV\n"
                 "Umbralización · Detección de Contornos · Análisis Morfológico",
                 color='white', fontsize=14, fontweight='bold', y=0.98,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#0f3460', alpha=0.8))

    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    plt.savefig("resultados_segmentacion.png", dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e')
    print("[INFO] Resultados guardados en: resultados_segmentacion.png")
    plt.show()


# ─────────────────────────────────────────────
# 8. PIPELINE PRINCIPAL
# ─────────────────────────────────────────────

def main():
    print("\n" + "═" * 50)
    print("  TALLER: SEGMENTACIÓN CON OPENCV")
    print("═" * 50)

    # Paso 1 — Cargar imagen
    # Para usar tu propia imagen: cargar_imagen("ruta/a/tu/imagen.jpg")
    ruta_imagen = sys.argv[1] if len(sys.argv) > 1 else None
    imagen_gris, imagen_color = cargar_imagen(ruta_imagen)

    # Paso 2 — Umbralización
    binaria_fija, binaria_otsu, valor_otsu = aplicar_umbral_fijo(imagen_gris, valor_umbral=127)
    binaria_media, binaria_gaussiana = aplicar_umbral_adaptativo(imagen_gris)

    # Paso 3 — Limpieza morfológica
    binaria_limpia = limpiar_imagen(binaria_otsu)

    # Paso 4 — Detección de contornos (sobre la binaria OTSU limpia)
    contornos = detectar_contornos(binaria_limpia, area_minima=800)

    # Paso 5 — Dibujar resultados
    imagen_resultado, datos_formas = dibujar_resultados(imagen_color, contornos)

    # Paso 6 — Métricas
    metricas = calcular_metricas(datos_formas)
    metricas['otsu'] = f"{valor_otsu:.1f}"

    # Paso 7 — Visualización
    visualizar_resultados(
        imagen_gris, imagen_color,
        binaria_fija, binaria_otsu,
        binaria_gaussiana, imagen_resultado,
        datos_formas, metricas
    )


if __name__ == "__main__":
    main()