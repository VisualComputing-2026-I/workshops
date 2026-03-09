/**
 * main.js
 * Punto de entrada de la aplicacion del taller Z-Buffer & Depth Testing.
 *
 * Funcionalidades:
 *  - Renderizado de escena 3D con objetos superpuestos
 *  - Toggle depth test ON/OFF con comparacion visual
 *  - Visualizacion del depth buffer (no-lineal y lineal) via shaders
 *  - Comparacion lado a lado (split-screen scissor test)
 *  - Demostracion y resolucion de Z-fighting
 *  - Ajuste dinamico de near/far para experimentar con precision
 */
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import {
  depthVertexShader,
  depthFragmentShader,
  linearDepthVertexShader,
  linearDepthFragmentShader,
} from "./shaders.js";
import { createSceneObjects, createLights } from "./scene-objects.js";
import { createGUI } from "./gui-controls.js";

// ========== Renderer ==========
const canvas = document.getElementById("webgl-canvas");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x0a0e17);
// Habilitar scissor test para la comparacion lado a lado
renderer.setScissorTest(false);

// ========== Escena & Camara ==========
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x0a0e17, 14, 50);

const camera = new THREE.PerspectiveCamera(
  55,
  window.innerWidth / window.innerHeight,
  0.1,
  60
);
camera.position.set(6, 4.5, 8);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 0.6, 0);
controls.autoRotate = true;
controls.autoRotateSpeed = 0.6;

// ========== Contenido de la escena ==========
const sceneData = createSceneObjects();
scene.add(sceneData.group);
scene.add(createLights());

// ========== Materiales de profundidad ==========
const depthMat = new THREE.ShaderMaterial({
  vertexShader: depthVertexShader,
  fragmentShader: depthFragmentShader,
});

const linearDepthMat = new THREE.ShaderMaterial({
  vertexShader: linearDepthVertexShader,
  fragmentShader: linearDepthFragmentShader,
  uniforms: {
    uNear: { value: camera.near },
    uFar: { value: camera.far },
  },
});

// Cache de materiales originales para restaurar
const materialCache = new Map();

function cacheOriginalMaterials() {
  sceneData.group.traverse((obj) => {
    if (obj.isMesh && !materialCache.has(obj.uuid)) {
      materialCache.set(obj.uuid, obj.material);
    }
  });
}
cacheOriginalMaterials();

// ========== Estado de la app ==========
let currentViewMode = "Normal";   // "Normal" | "Depth" | "Depth Lineal"
let comparisonMode = false;

// Referencias DOM
const infoText = document.getElementById("info-text");
const depthBadge = document.getElementById("depth-status");
const viewBadge = document.getElementById("view-status");
const comparisonOverlay = document.getElementById("comparison-overlay");

// ========== Funciones de control ==========

/** Aplica o quita depthTest/depthWrite a todos los meshes */
function setDepthTest(enabled) {
  sceneData.group.traverse((obj) => {
    if (!obj.isMesh) return;
    obj.material.depthTest = enabled;
    obj.material.depthWrite = enabled;
    obj.material.needsUpdate = true;
  });

  // Actualizar UI
  depthBadge.textContent = `Depth Test: ${enabled ? "ON" : "OFF"}`;
  depthBadge.className = `badge ${enabled ? "badge-on" : "badge-off"}`;
  infoText.textContent = enabled
    ? "Depth testing activado — oclusion correcta basada en Z-buffer."
    : "Depth testing DESACTIVADO — los objetos se pintan por orden de draw call, causando artefactos de oclusion.";
}

/** Cambia el modo de visualizacion de materiales */
function setViewMode(mode) {
  currentViewMode = mode;

  sceneData.group.traverse((obj) => {
    if (!obj.isMesh) return;
    switch (mode) {
      case "Normal":
        obj.material = materialCache.get(obj.uuid);
        break;
      case "Depth":
        obj.material = depthMat;
        break;
      case "Depth Lineal":
        obj.material = linearDepthMat;
        break;
    }
  });

  // Actualizar badge
  if (mode === "Normal") {
    viewBadge.textContent = "Vista: Normal";
    viewBadge.className = "badge badge-normal";
    infoText.textContent = "Vista normal con materiales estandar.";
  } else if (mode === "Depth") {
    viewBadge.textContent = "Vista: Depth (no-lineal)";
    viewBadge.className = "badge badge-depth";
    infoText.textContent =
      "Shader: gl_FragColor = vec4(vec3(gl_FragCoord.z), 1.0) — profundidad no-lineal del GPU.";
  } else {
    viewBadge.textContent = "Vista: Depth Lineal";
    viewBadge.className = "badge badge-depth";
    infoText.textContent =
      "Profundidad linealizada con near/far. Mas uniforme que la representacion nativa.";
  }
}

/** Activa/desactiva la comparacion lado a lado */
function setComparison(enabled) {
  comparisonMode = enabled;
  renderer.setScissorTest(enabled);
  comparisonOverlay.classList.toggle("hidden", !enabled);
  if (enabled) {
    infoText.textContent =
      "Comparacion: izquierda SIN depth test, derecha CON depth test.";
  }
}

/** Ajusta camera near */
function setNear(value) {
  camera.near = value;
  camera.updateProjectionMatrix();
  linearDepthMat.uniforms.uNear.value = value;
}

/** Ajusta camera far */
function setFar(value) {
  camera.far = Math.max(value, camera.near + 0.1);
  camera.updateProjectionMatrix();
  linearDepthMat.uniforms.uFar.value = camera.far;
  scene.fog.far = camera.far * 0.85;
}

/** Muestra/oculta los planos de Z-fighting */
function setZFightingVisible(visible) {
  sceneData.zFightGroup.visible = visible;
}

/** Resuelve Z-fighting con polygonOffset */
function solveZFighting(solve) {
  const mat = sceneData.planeB.material;
  if (solve) {
    mat.polygonOffset = true;
    mat.polygonOffsetFactor = -1;
    mat.polygonOffsetUnits = -1;
    // Tambien separar ligeramente como alternativa adicional
    sceneData.planeB.position.z = -1.995;
    infoText.textContent =
      "Z-fighting resuelto con polygonOffset y separacion minima entre planos.";
  } else {
    mat.polygonOffset = false;
    mat.polygonOffsetFactor = 0;
    mat.polygonOffsetUnits = 0;
    sceneData.planeB.position.z = -1.999;
    infoText.textContent =
      "Z-fighting activo: dos planos casi coplanares compiten por el mismo pixel.";
  }
  mat.needsUpdate = true;
}

// ========== GUI ==========
createGUI({
  onDepthTestToggle: setDepthTest,
  onViewModeChange: setViewMode,
  onComparisonToggle: setComparison,
  onNearChange: setNear,
  onFarChange: setFar,
  onZFightingVisibility: setZFightingVisible,
  onZFightingSolve: solveZFighting,
  onAutoRotate: (v) => {
    controls.autoRotate = v;
  },
});

// ========== Animacion ==========
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // Rotar objetos suavemente
  sceneData.animatedObjects.forEach((obj, i) => {
    const speed = 0.25 + i * 0.12;
    obj.rotation.y = t * speed;
    if (obj.name === "torus") {
      obj.rotation.x = Math.PI / 3 + Math.sin(t * 0.4) * 0.3;
    }
  });

  controls.update();

  if (comparisonMode) {
    renderComparison();
  } else {
    // Render normal a pantalla completa
    renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    renderer.setScissor(0, 0, window.innerWidth, window.innerHeight);
    renderer.render(scene, camera);
  }
}

/**
 * Renderiza la escena dos veces lado a lado:
 *  - Mitad izquierda: SIN depth test
 *  - Mitad derecha:  CON depth test
 */
function renderComparison() {
  const halfW = Math.floor(window.innerWidth / 2);
  const h = window.innerHeight;

  // --- IZQUIERDA: sin depth test ---
  renderer.setViewport(0, 0, halfW, h);
  renderer.setScissor(0, 0, halfW, h);
  setDepthTestSilent(false);
  renderer.render(scene, camera);

  // --- DERECHA: con depth test ---
  renderer.setViewport(halfW, 0, window.innerWidth - halfW, h);
  renderer.setScissor(halfW, 0, window.innerWidth - halfW, h);
  setDepthTestSilent(true);
  renderer.render(scene, camera);
}

/** Cambia depthTest sin actualizar UI (usado internamente para split) */
function setDepthTestSilent(enabled) {
  sceneData.group.traverse((obj) => {
    if (!obj.isMesh) return;
    obj.material.depthTest = enabled;
    obj.material.depthWrite = enabled;
    obj.material.needsUpdate = true;
  });
}

animate();

// ========== Resize ==========
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
