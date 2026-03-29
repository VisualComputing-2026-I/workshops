/**
 * scene-objects.js
 * Crea esferas con diferentes modelos de iluminacion para comparacion visual.
 *
 * Disposicion:
 *  - 4 esferas principales: Lambert, Phong, Blinn-Phong, PBR
 *  - Fila de esferas PBR con diferentes valores de metalness/roughness
 *  - Luz puntual movil
 */
import * as THREE from "three";
import {
  lambertVertexShader,
  lambertFragmentShader,
  phongVertexShader,
  phongFragmentShader,
  blinnPhongVertexShader,
  blinnPhongFragmentShader,
  pbrVertexShader,
  pbrFragmentShader,
  vectorVisVertexShader,
  vectorVisFragmentShader,
} from "./shaders.js";

// Parametros de luz compartidos
const lightParams = {
  position: new THREE.Vector3(4, 5, 4),
  color: new THREE.Color(1, 1, 1),
  intensity: 1.0,
};

// Parametros de material por defecto
const defaultMaterialParams = {
  ambient: new THREE.Color(0.1, 0.1, 0.15),
  diffuse: new THREE.Color(0.8, 0.2, 0.2),
  specular: new THREE.Color(1.0, 1.0, 1.0),
  shininess: 32.0,
};

/**
 * Crea un ShaderMaterial para Lambert
 */
export function createLambertMaterial(camera, diffuseColor = null) {
  return new THREE.ShaderMaterial({
    vertexShader: lambertVertexShader,
    fragmentShader: lambertFragmentShader,
    uniforms: {
      uLightPosition: { value: lightParams.position.clone() },
      uLightColor: { value: lightParams.color.clone() },
      uLightIntensity: { value: lightParams.intensity },
      uAmbientColor: { value: defaultMaterialParams.ambient.clone() },
      uDiffuseColor: {
        value: diffuseColor
          ? new THREE.Color(diffuseColor)
          : defaultMaterialParams.diffuse.clone(),
      },
    },
  });
}

/**
 * Crea un ShaderMaterial para Phong
 */
export function createPhongMaterial(camera, diffuseColor = null) {
  return new THREE.ShaderMaterial({
    vertexShader: phongVertexShader,
    fragmentShader: phongFragmentShader,
    uniforms: {
      uLightPosition: { value: lightParams.position.clone() },
      uLightColor: { value: lightParams.color.clone() },
      uLightIntensity: { value: lightParams.intensity },
      uAmbientColor: { value: defaultMaterialParams.ambient.clone() },
      uDiffuseColor: {
        value: diffuseColor
          ? new THREE.Color(diffuseColor)
          : defaultMaterialParams.diffuse.clone(),
      },
      uSpecularColor: { value: defaultMaterialParams.specular.clone() },
      uShininess: { value: defaultMaterialParams.shininess },
      uCameraPosition: { value: camera.position.clone() },
    },
  });
}

/**
 * Crea un ShaderMaterial para Blinn-Phong
 */
export function createBlinnPhongMaterial(camera, diffuseColor = null) {
  return new THREE.ShaderMaterial({
    vertexShader: blinnPhongVertexShader,
    fragmentShader: blinnPhongFragmentShader,
    uniforms: {
      uLightPosition: { value: lightParams.position.clone() },
      uLightColor: { value: lightParams.color.clone() },
      uLightIntensity: { value: lightParams.intensity },
      uAmbientColor: { value: defaultMaterialParams.ambient.clone() },
      uDiffuseColor: {
        value: diffuseColor
          ? new THREE.Color(diffuseColor)
          : defaultMaterialParams.diffuse.clone(),
      },
      uSpecularColor: { value: defaultMaterialParams.specular.clone() },
      uShininess: { value: defaultMaterialParams.shininess },
      uCameraPosition: { value: camera.position.clone() },
    },
  });
}

/**
 * Crea un ShaderMaterial para PBR
 */
export function createPBRMaterial(
  camera,
  albedo = 0xe63946,
  metalness = 0.0,
  roughness = 0.5
) {
  return new THREE.ShaderMaterial({
    vertexShader: pbrVertexShader,
    fragmentShader: pbrFragmentShader,
    uniforms: {
      uLightPosition: { value: lightParams.position.clone() },
      uLightColor: { value: lightParams.color.clone() },
      uLightIntensity: { value: lightParams.intensity },
      uAlbedo: { value: new THREE.Color(albedo) },
      uMetalness: { value: metalness },
      uRoughness: { value: roughness },
      uCameraPosition: { value: camera.position.clone() },
    },
  });
}

/**
 * Crea material para visualizar vectores
 */
export function createVectorVisMaterial(camera) {
  return new THREE.ShaderMaterial({
    vertexShader: vectorVisVertexShader,
    fragmentShader: vectorVisFragmentShader,
    uniforms: {
      uLightPosition: { value: lightParams.position.clone() },
      uCameraPosition: { value: camera.position.clone() },
      uVectorMode: { value: 0 },
    },
  });
}

/**
 * Crea todos los objetos de la escena principal
 */
export function createSceneObjects(camera) {
  const group = new THREE.Group();
  const sphereGeo = new THREE.SphereGeometry(1.2, 64, 64);

  // Esferas principales con diferentes modelos de iluminacion
  const sphereLambert = new THREE.Mesh(sphereGeo, createLambertMaterial(camera));
  sphereLambert.position.set(-5, 0, 0);
  sphereLambert.name = "lambert";
  sphereLambert.userData.label = "Lambert (Diffuse)";
  group.add(sphereLambert);

  const spherePhong = new THREE.Mesh(sphereGeo, createPhongMaterial(camera));
  spherePhong.position.set(-1.7, 0, 0);
  spherePhong.name = "phong";
  spherePhong.userData.label = "Phong";
  group.add(spherePhong);

  const sphereBlinn = new THREE.Mesh(sphereGeo, createBlinnPhongMaterial(camera));
  sphereBlinn.position.set(1.7, 0, 0);
  sphereBlinn.name = "blinn-phong";
  sphereBlinn.userData.label = "Blinn-Phong";
  group.add(sphereBlinn);

  const spherePBR = new THREE.Mesh(sphereGeo, createPBRMaterial(camera, 0xe63946, 0.0, 0.4));
  spherePBR.position.set(5, 0, 0);
  spherePBR.name = "pbr";
  spherePBR.userData.label = "PBR";
  group.add(spherePBR);

  // Array de esferas principales para actualizacion
  const mainSpheres = [sphereLambert, spherePhong, sphereBlinn, spherePBR];

  // Fila de esferas PBR con variaciones de metalness/roughness
  const pbrVariations = new THREE.Group();
  pbrVariations.position.set(0, -3.5, 0);

  const smallSphereGeo = new THREE.SphereGeometry(0.7, 48, 48);
  const pbrSpheres = [];

  // Fila superior: Variaciones de roughness (dielectrico)
  for (let i = 0; i < 5; i++) {
    const roughness = i * 0.25;
    const mat = createPBRMaterial(camera, 0x3b82f6, 0.0, roughness);
    const sphere = new THREE.Mesh(smallSphereGeo, mat);
    sphere.position.set(-4 + i * 2, 1.5, 0);
    sphere.name = `pbr-dielectric-r${roughness}`;
    sphere.userData.label = `Roughness: ${roughness.toFixed(2)}`;
    pbrVariations.add(sphere);
    pbrSpheres.push(sphere);
  }

  // Fila inferior: Variaciones de roughness (metal)
  for (let i = 0; i < 5; i++) {
    const roughness = i * 0.25;
    const mat = createPBRMaterial(camera, 0xfbbf24, 1.0, roughness);
    const sphere = new THREE.Mesh(smallSphereGeo, mat);
    sphere.position.set(-4 + i * 2, 0, 0);
    sphere.name = `pbr-metal-r${roughness}`;
    sphere.userData.label = `Metal R: ${roughness.toFixed(2)}`;
    pbrVariations.add(sphere);
    pbrSpheres.push(sphere);
  }

  group.add(pbrVariations);

  // Suelo
  const floorGeo = new THREE.PlaneGeometry(30, 30);
  const floorMat = new THREE.MeshStandardMaterial({
    color: 0x1e293b,
    roughness: 0.85,
    metalness: 0.05,
  });
  const floor = new THREE.Mesh(floorGeo, floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -1.6;
  floor.receiveShadow = true;
  group.add(floor);

  // Indicador visual de luz
  const lightIndicator = new THREE.Mesh(
    new THREE.SphereGeometry(0.15, 16, 16),
    new THREE.MeshBasicMaterial({ color: 0xffffff })
  );
  lightIndicator.position.copy(lightParams.position);
  lightIndicator.name = "light-indicator";
  group.add(lightIndicator);

  return {
    group,
    mainSpheres,
    pbrSpheres,
    pbrVariations,
    lightIndicator,
    lightParams,
    floor,
  };
}

/**
 * Crea las luces de la escena
 */
export function createLights() {
  const lights = new THREE.Group();

  // Luz hemisferica para ambiente
  const hemi = new THREE.HemisphereLight(0xffffff, 0x1a1f2e, 0.4);
  lights.add(hemi);

  // Luz direccional sutil
  const dir = new THREE.DirectionalLight(0xffffff, 0.3);
  dir.position.set(10, 10, 5);
  lights.add(dir);

  return lights;
}

/**
 * Actualiza la posicion de la luz en todos los materiales
 */
export function updateLightPosition(sceneData, position) {
  sceneData.lightParams.position.copy(position);
  sceneData.lightIndicator.position.copy(position);

  // Actualizar en esferas principales
  sceneData.mainSpheres.forEach((sphere) => {
    if (sphere.material.uniforms && sphere.material.uniforms.uLightPosition) {
      sphere.material.uniforms.uLightPosition.value.copy(position);
    }
  });

  // Actualizar en esferas PBR
  sceneData.pbrSpheres.forEach((sphere) => {
    if (sphere.material.uniforms && sphere.material.uniforms.uLightPosition) {
      sphere.material.uniforms.uLightPosition.value.copy(position);
    }
  });
}

/**
 * Actualiza la posicion de la camara en los materiales que lo necesitan
 */
export function updateCameraPosition(sceneData, camera) {
  const allSpheres = [...sceneData.mainSpheres, ...sceneData.pbrSpheres];
  allSpheres.forEach((sphere) => {
    if (sphere.material.uniforms && sphere.material.uniforms.uCameraPosition) {
      sphere.material.uniforms.uCameraPosition.value.copy(camera.position);
    }
  });
}

/**
 * Crea etiquetas de texto para cada esfera
 */
export function createLabels(mainSpheres) {
  const labels = [];

  mainSpheres.forEach((sphere) => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    canvas.width = 256;
    canvas.height = 64;

    ctx.fillStyle = "rgba(10, 14, 23, 0.8)";
    ctx.fillRect(0, 0, 256, 64);
    ctx.fillStyle = "#e2e8f0";
    ctx.font = "bold 24px Segoe UI, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(sphere.userData.label, 128, 40);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMat);
    sprite.position.copy(sphere.position);
    sprite.position.y += 2.0;
    sprite.scale.set(2.5, 0.625, 1);

    labels.push(sprite);
  });

  return labels;
}
