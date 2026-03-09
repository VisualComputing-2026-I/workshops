/**
 * gui-controls.js
 * Panel de controles (lil-gui) para experimentar con Z-buffer en tiempo real.
 *
 * Controles expuestos:
 *  1. Depth Test ON/OFF
 *  2. Vista: Normal / Depth (no-lineal) / Depth Lineal
 *  3. Camera Near  (0.01 - 10)
 *  4. Camera Far   (5 - 500)
 *  5. Mostrar Z-fighting
 *  6. Resolver Z-fighting (polygonOffset)
 *  7. Comparacion lado a lado (split-screen)
 *  8. Rotacion automatica
 */
import GUI from "lil-gui";

/**
 * @param {object} callbacks – funciones callback para cada control
 */
export function createGUI(callbacks) {
  const params = {
    depthTest: true,
    viewMode: "Normal",         // "Normal" | "Depth" | "Depth Lineal"
    near: 0.1,
    far: 60,
    showZFighting: true,
    solveZFighting: false,
    comparison: false,
    autoRotate: true,
  };

  const gui = new GUI({ title: "⚙️ Controles Z-Buffer", width: 280 });

  // --- Carpeta: Depth Testing ---
  const fDepth = gui.addFolder("Depth Testing");

  fDepth.add(params, "depthTest").name("Depth Test").onChange((v) => {
    callbacks.onDepthTestToggle(v);
  });

  fDepth.add(params, "viewMode", ["Normal", "Depth", "Depth Lineal"])
    .name("Modo de vista")
    .onChange((v) => {
      callbacks.onViewModeChange(v);
    });

  fDepth.add(params, "comparison").name("Comparar (split)").onChange((v) => {
    callbacks.onComparisonToggle(v);
  });

  fDepth.open();

  // --- Carpeta: Camera ---
  const fCam = gui.addFolder("Cámara (near / far)");

  fCam.add(params, "near", 0.01, 10, 0.01).name("Near Plane").onChange((v) => {
    callbacks.onNearChange(v);
  });

  fCam.add(params, "far", 2, 500, 0.5).name("Far Plane").onChange((v) => {
    callbacks.onFarChange(v);
  });

  fCam.open();

  // --- Carpeta: Z-Fighting ---
  const fZF = gui.addFolder("Z-Fighting");

  fZF.add(params, "showZFighting").name("Mostrar planos").onChange((v) => {
    callbacks.onZFightingVisibility(v);
  });

  fZF.add(params, "solveZFighting").name("Resolver (offset)").onChange((v) => {
    callbacks.onZFightingSolve(v);
  });

  fZF.open();

  // --- Carpeta: Escena ---
  const fScene = gui.addFolder("Escena");

  fScene.add(params, "autoRotate").name("Auto-rotar").onChange((v) => {
    callbacks.onAutoRotate(v);
  });

  return { gui, params };
}
