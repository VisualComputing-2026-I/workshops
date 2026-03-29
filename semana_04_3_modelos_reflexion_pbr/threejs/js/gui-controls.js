/**
 * gui-controls.js
 * Panel de controles interactivos para experimentar con modelos de iluminacion.
 *
 * Controles:
 *  - Parametros de luz (posicion, color, intensidad)
 *  - Parametros de material (diffuse, specular, shininess)
 *  - Parametros PBR (metalness, roughness)
 *  - Modo de visualizacion (Normal, Solo Diffuse, Solo Specular, Vectores)
 *  - Preset de materiales (plastico, metal, etc)
 */
import GUI from "lil-gui";
import * as THREE from "three";

/**
 * @param {object} callbacks - Funciones callback para cada control
 */
export function createGUI(callbacks) {
  const params = {
    // Luz
    lightX: 4,
    lightY: 5,
    lightZ: 4,
    lightIntensity: 1.0,
    lightColor: "#ffffff",
    animateLight: true,

    // Material clasico
    diffuseColor: "#cc2936",
    specularColor: "#ffffff",
    shininess: 32,
    ambientIntensity: 0.1,

    // PBR
    albedo: "#e63946",
    metalness: 0.0,
    roughness: 0.4,

    // Visualizacion
    viewMode: "Todos los modelos",
    vectorMode: "Normal",
    showLabels: true,
    showPBRGrid: true,

    // Presets
    preset: "Plastico rojo",

    // Escena
    autoRotate: false,
  };

  const gui = new GUI({ title: "Modelos de Iluminacion", width: 300 });

  // ========== Carpeta: Luz ==========
  const fLight = gui.addFolder("Luz");

  fLight.add(params, "lightX", -10, 10, 0.1).name("Posicion X").onChange(() => {
    callbacks.onLightPositionChange(params.lightX, params.lightY, params.lightZ);
  });

  fLight.add(params, "lightY", 0, 15, 0.1).name("Posicion Y").onChange(() => {
    callbacks.onLightPositionChange(params.lightX, params.lightY, params.lightZ);
  });

  fLight.add(params, "lightZ", -10, 10, 0.1).name("Posicion Z").onChange(() => {
    callbacks.onLightPositionChange(params.lightX, params.lightY, params.lightZ);
  });

  fLight.add(params, "lightIntensity", 0, 3, 0.05).name("Intensidad").onChange((v) => {
    callbacks.onLightIntensityChange(v);
  });

  fLight.addColor(params, "lightColor").name("Color").onChange((v) => {
    callbacks.onLightColorChange(v);
  });

  fLight.add(params, "animateLight").name("Animar luz").onChange((v) => {
    callbacks.onAnimateLightChange(v);
  });

  fLight.open();

  // ========== Carpeta: Material Clasico ==========
  const fMaterial = gui.addFolder("Material (Lambert/Phong)");

  fMaterial.addColor(params, "diffuseColor").name("Color Diffuse").onChange((v) => {
    callbacks.onDiffuseColorChange(v);
  });

  fMaterial.addColor(params, "specularColor").name("Color Specular").onChange((v) => {
    callbacks.onSpecularColorChange(v);
  });

  fMaterial.add(params, "shininess", 1, 256, 1).name("Shininess").onChange((v) => {
    callbacks.onShininessChange(v);
  });

  fMaterial.add(params, "ambientIntensity", 0, 0.5, 0.01).name("Ambiente").onChange((v) => {
    callbacks.onAmbientChange(v);
  });

  fMaterial.open();

  // ========== Carpeta: PBR ==========
  const fPBR = gui.addFolder("PBR");

  fPBR.addColor(params, "albedo").name("Albedo").onChange((v) => {
    callbacks.onAlbedoChange(v);
  });

  fPBR.add(params, "metalness", 0, 1, 0.01).name("Metalness").onChange((v) => {
    callbacks.onMetalnessChange(v);
  });

  fPBR.add(params, "roughness", 0.01, 1, 0.01).name("Roughness").onChange((v) => {
    callbacks.onRoughnessChange(v);
  });

  fPBR.open();

  // ========== Carpeta: Visualizacion ==========
  const fView = gui.addFolder("Visualizacion");

  fView
    .add(params, "viewMode", [
      "Todos los modelos",
      "Solo Lambert",
      "Solo Phong",
      "Solo Blinn-Phong",
      "Solo PBR",
      "Comparar Phong vs Blinn",
      "Visualizar Vectores",
    ])
    .name("Modo Vista")
    .onChange((v) => {
      callbacks.onViewModeChange(v);
    });

  fView
    .add(params, "vectorMode", ["Normal", "Light Dir", "View Dir", "Reflect", "Half Vector"])
    .name("Vector")
    .onChange((v) => {
      callbacks.onVectorModeChange(v);
    });

  fView.add(params, "showLabels").name("Mostrar etiquetas").onChange((v) => {
    callbacks.onShowLabelsChange(v);
  });

  fView.add(params, "showPBRGrid").name("Mostrar grid PBR").onChange((v) => {
    callbacks.onShowPBRGridChange(v);
  });

  fView.open();

  // ========== Carpeta: Presets ==========
  const fPresets = gui.addFolder("Presets de Material");

  fPresets
    .add(params, "preset", [
      "Plastico rojo",
      "Plastico azul",
      "Metal dorado",
      "Metal cromado",
      "Goma mate",
      "Ceramica",
      "Piel",
    ])
    .name("Preset")
    .onChange((v) => {
      applyPreset(v, params, callbacks);
    });

  // ========== Carpeta: Escena ==========
  const fScene = gui.addFolder("Escena");

  fScene.add(params, "autoRotate").name("Auto-rotar").onChange((v) => {
    callbacks.onAutoRotateChange(v);
  });

  return { gui, params };
}

/**
 * Aplica presets de materiales predefinidos
 */
function applyPreset(presetName, params, callbacks) {
  const presets = {
    "Plastico rojo": {
      diffuse: "#cc2936",
      specular: "#ffffff",
      shininess: 32,
      albedo: "#cc2936",
      metalness: 0.0,
      roughness: 0.4,
    },
    "Plastico azul": {
      diffuse: "#1e6091",
      specular: "#ffffff",
      shininess: 48,
      albedo: "#1e6091",
      metalness: 0.0,
      roughness: 0.35,
    },
    "Metal dorado": {
      diffuse: "#d4a855",
      specular: "#ffeaa7",
      shininess: 100,
      albedo: "#d4a855",
      metalness: 1.0,
      roughness: 0.3,
    },
    "Metal cromado": {
      diffuse: "#a0a0a0",
      specular: "#ffffff",
      shininess: 200,
      albedo: "#c0c0c0",
      metalness: 1.0,
      roughness: 0.1,
    },
    "Goma mate": {
      diffuse: "#2d3436",
      specular: "#2d3436",
      shininess: 5,
      albedo: "#2d3436",
      metalness: 0.0,
      roughness: 0.95,
    },
    Ceramica: {
      diffuse: "#f5f0e6",
      specular: "#ffffff",
      shininess: 60,
      albedo: "#f5f0e6",
      metalness: 0.0,
      roughness: 0.5,
    },
    Piel: {
      diffuse: "#b5651d",
      specular: "#8b4513",
      shininess: 15,
      albedo: "#b5651d",
      metalness: 0.0,
      roughness: 0.7,
    },
  };

  const preset = presets[presetName];
  if (!preset) return;

  // Actualizar parametros y callbacks
  params.diffuseColor = preset.diffuse;
  params.specularColor = preset.specular;
  params.shininess = preset.shininess;
  params.albedo = preset.albedo;
  params.metalness = preset.metalness;
  params.roughness = preset.roughness;

  callbacks.onDiffuseColorChange(preset.diffuse);
  callbacks.onSpecularColorChange(preset.specular);
  callbacks.onShininessChange(preset.shininess);
  callbacks.onAlbedoChange(preset.albedo);
  callbacks.onMetalnessChange(preset.metalness);
  callbacks.onRoughnessChange(preset.roughness);
}
