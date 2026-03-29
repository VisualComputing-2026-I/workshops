/**
 * main.js
 * Punto de entrada del taller de Modelos de Reflexion: Lambert, Phong y PBR.
 *
 * Funcionalidades:
 *  - Comparacion visual de Lambert, Phong, Blinn-Phong y PBR
 *  - Ajuste interactivo de parametros de luz y material
 *  - Visualizacion de vectores (N, L, V, R, H)
 *  - Grid de esferas PBR con variaciones de metalness/roughness
 *  - Presets de materiales (plastico, metal, etc)
 */
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import {
  createSceneObjects,
  createLights,
  updateLightPosition,
  updateCameraPosition,
  createLabels,
  createLambertMaterial,
  createPhongMaterial,
  createBlinnPhongMaterial,
  createPBRMaterial,
  createVectorVisMaterial,
} from "./scene-objects.js";
import { createGUI } from "./gui-controls.js";

// ========== Renderer ==========
const canvas = document.getElementById("webgl-canvas");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x0a0e17);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// ========== Escena & Camara ==========
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x0a0e17, 20, 50);

const camera = new THREE.PerspectiveCamera(
  50,
  window.innerWidth / window.innerHeight,
  0.1,
  100
);
camera.position.set(0, 4, 14);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 0, 0);
controls.autoRotate = false;
controls.autoRotateSpeed = 0.5;

// ========== Contenido de la escena ==========
const sceneData = createSceneObjects(camera);
scene.add(sceneData.group);
scene.add(createLights());

// Crear etiquetas
const labels = createLabels(sceneData.mainSpheres);
const labelsGroup = new THREE.Group();
labels.forEach((label) => labelsGroup.add(label));
scene.add(labelsGroup);

// Material para visualizacion de vectores
let vectorVisMaterial = createVectorVisMaterial(camera);

// Cache de materiales originales
const materialCache = new Map();
sceneData.mainSpheres.forEach((sphere) => {
  materialCache.set(sphere.uuid, sphere.material);
});

// ========== Estado de la app ==========
let animateLight = true;
let currentViewMode = "Todos los modelos";

// Referencias DOM
const infoText = document.getElementById("info-text");
const equationText = document.getElementById("equation-text");

// ========== Funciones de control ==========

function setLightPosition(x, y, z) {
  const pos = new THREE.Vector3(x, y, z);
  updateLightPosition(sceneData, pos);
}

function setLightIntensity(intensity) {
  const allSpheres = [...sceneData.mainSpheres, ...sceneData.pbrSpheres];
  allSpheres.forEach((sphere) => {
    if (sphere.material.uniforms && sphere.material.uniforms.uLightIntensity) {
      sphere.material.uniforms.uLightIntensity.value = intensity;
    }
  });
}

function setLightColor(colorHex) {
  const color = new THREE.Color(colorHex);
  const allSpheres = [...sceneData.mainSpheres, ...sceneData.pbrSpheres];
  allSpheres.forEach((sphere) => {
    if (sphere.material.uniforms && sphere.material.uniforms.uLightColor) {
      sphere.material.uniforms.uLightColor.value.copy(color);
    }
  });
  sceneData.lightIndicator.material.color.copy(color);
}

function setDiffuseColor(colorHex) {
  const color = new THREE.Color(colorHex);
  sceneData.mainSpheres.forEach((sphere) => {
    if (
      sphere.material.uniforms &&
      sphere.material.uniforms.uDiffuseColor &&
      sphere.name !== "pbr"
    ) {
      sphere.material.uniforms.uDiffuseColor.value.copy(color);
    }
  });
}

function setSpecularColor(colorHex) {
  const color = new THREE.Color(colorHex);
  sceneData.mainSpheres.forEach((sphere) => {
    if (sphere.material.uniforms && sphere.material.uniforms.uSpecularColor) {
      sphere.material.uniforms.uSpecularColor.value.copy(color);
    }
  });
}

function setShininess(value) {
  sceneData.mainSpheres.forEach((sphere) => {
    if (sphere.material.uniforms && sphere.material.uniforms.uShininess) {
      sphere.material.uniforms.uShininess.value = value;
    }
  });
  updateInfoText();
}

function setAmbientIntensity(value) {
  const ambient = new THREE.Color(value, value, value * 1.5);
  sceneData.mainSpheres.forEach((sphere) => {
    if (sphere.material.uniforms && sphere.material.uniforms.uAmbientColor) {
      sphere.material.uniforms.uAmbientColor.value.copy(ambient);
    }
  });
}

function setAlbedo(colorHex) {
  const color = new THREE.Color(colorHex);
  const pbrSphere = sceneData.mainSpheres.find((s) => s.name === "pbr");
  if (pbrSphere && pbrSphere.material.uniforms) {
    pbrSphere.material.uniforms.uAlbedo.value.copy(color);
  }
}

function setMetalness(value) {
  const pbrSphere = sceneData.mainSpheres.find((s) => s.name === "pbr");
  if (pbrSphere && pbrSphere.material.uniforms) {
    pbrSphere.material.uniforms.uMetalness.value = value;
  }
  updateInfoText();
}

function setRoughness(value) {
  const pbrSphere = sceneData.mainSpheres.find((s) => s.name === "pbr");
  if (pbrSphere && pbrSphere.material.uniforms) {
    pbrSphere.material.uniforms.uRoughness.value = value;
  }
  updateInfoText();
}

function setViewMode(mode) {
  currentViewMode = mode;

  // Restaurar materiales originales
  sceneData.mainSpheres.forEach((sphere) => {
    sphere.material = materialCache.get(sphere.uuid);
    sphere.visible = true;
  });

  switch (mode) {
    case "Todos los modelos":
      // Todos visibles
      break;
    case "Solo Lambert":
      sceneData.mainSpheres.forEach((s) => {
        s.visible = s.name === "lambert";
      });
      break;
    case "Solo Phong":
      sceneData.mainSpheres.forEach((s) => {
        s.visible = s.name === "phong";
      });
      break;
    case "Solo Blinn-Phong":
      sceneData.mainSpheres.forEach((s) => {
        s.visible = s.name === "blinn-phong";
      });
      break;
    case "Solo PBR":
      sceneData.mainSpheres.forEach((s) => {
        s.visible = s.name === "pbr";
      });
      break;
    case "Comparar Phong vs Blinn":
      sceneData.mainSpheres.forEach((s) => {
        s.visible = s.name === "phong" || s.name === "blinn-phong";
      });
      break;
    case "Visualizar Vectores":
      sceneData.mainSpheres.forEach((sphere) => {
        sphere.material = vectorVisMaterial;
        sphere.visible = true;
      });
      break;
  }

  updateInfoText();
}

function setVectorMode(mode) {
  const modeMap = {
    Normal: 0,
    "Light Dir": 1,
    "View Dir": 2,
    Reflect: 3,
    "Half Vector": 4,
  };
  vectorVisMaterial.uniforms.uVectorMode.value = modeMap[mode] || 0;
}

function setShowLabels(show) {
  labelsGroup.visible = show;
}

function setShowPBRGrid(show) {
  sceneData.pbrVariations.visible = show;
}

function updateInfoText() {
  if (!infoText) return;

  const equations = {
    lambert: "I = k_a + k_d * max(N . L, 0)",
    phong: "I = k_a + k_d * max(N . L, 0) + k_s * max(R . V, 0)^n",
    "blinn-phong": "I = k_a + k_d * max(N . L, 0) + k_s * max(N . H, 0)^n",
    pbr: "f_r = k_d * (c/pi) + (D * F * G) / (4 * (N.V) * (N.L))",
  };

  switch (currentViewMode) {
    case "Todos los modelos":
      infoText.textContent = "Comparacion de modelos de iluminacion";
      if (equationText) equationText.textContent = "";
      break;
    case "Solo Lambert":
      infoText.textContent = "Lambert: Solo componente difusa";
      if (equationText) equationText.textContent = equations.lambert;
      break;
    case "Solo Phong":
      infoText.textContent = "Phong: Diffuse + Specular (R . V)";
      if (equationText) equationText.textContent = equations.phong;
      break;
    case "Solo Blinn-Phong":
      infoText.textContent = "Blinn-Phong: Diffuse + Specular (N . H)";
      if (equationText) equationText.textContent = equations["blinn-phong"];
      break;
    case "Solo PBR":
      infoText.textContent = "PBR: Cook-Torrance BRDF";
      if (equationText) equationText.textContent = equations.pbr;
      break;
    case "Comparar Phong vs Blinn":
      infoText.textContent =
        "Izq: Phong (usa R=reflect), Der: Blinn-Phong (usa H=halfway)";
      if (equationText)
        equationText.textContent = "Blinn-Phong es mas eficiente y realista";
      break;
    case "Visualizar Vectores":
      infoText.textContent = "Vectores mapeados a RGB (componentes -1..1 -> 0..1)";
      if (equationText) equationText.textContent = "";
      break;
  }
}

// ========== GUI ==========
const { gui, params } = createGUI({
  onLightPositionChange: setLightPosition,
  onLightIntensityChange: setLightIntensity,
  onLightColorChange: setLightColor,
  onAnimateLightChange: (v) => {
    animateLight = v;
  },
  onDiffuseColorChange: setDiffuseColor,
  onSpecularColorChange: setSpecularColor,
  onShininessChange: setShininess,
  onAmbientChange: setAmbientIntensity,
  onAlbedoChange: setAlbedo,
  onMetalnessChange: setMetalness,
  onRoughnessChange: setRoughness,
  onViewModeChange: setViewMode,
  onVectorModeChange: setVectorMode,
  onShowLabelsChange: setShowLabels,
  onShowPBRGridChange: setShowPBRGrid,
  onAutoRotateChange: (v) => {
    controls.autoRotate = v;
  },
});

// ========== Animacion ==========
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // Animar luz circularmente
  if (animateLight) {
    const radius = 6;
    const speed = 0.5;
    const x = Math.sin(t * speed) * radius;
    const z = Math.cos(t * speed) * radius;
    setLightPosition(x, 5, z);

    // Actualizar params del GUI (sin trigger de callbacks)
    params.lightX = x;
    params.lightZ = z;
  }

  // Actualizar posicion de camara en materiales
  updateCameraPosition(sceneData, camera);

  // Actualizar vector vis material
  if (currentViewMode === "Visualizar Vectores") {
    vectorVisMaterial.uniforms.uCameraPosition.value.copy(camera.position);
    vectorVisMaterial.uniforms.uLightPosition.value.copy(
      sceneData.lightParams.position
    );
  }

  controls.update();
  renderer.render(scene, camera);
}

animate();

// ========== Resize ==========
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Inicializar texto informativo
updateInfoText();
