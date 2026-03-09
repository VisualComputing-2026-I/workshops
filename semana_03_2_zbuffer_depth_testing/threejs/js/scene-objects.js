/**
 * scene-objects.js
 * Crea y gestiona todos los objetos 3D de la escena del taller.
 *
 * Incluye:
 *  - Grupo principal con cubo, esfera, cono y torus superpuestos
 *  - Par de planos coplanares para demostrar Z-fighting
 *  - Suelo de referencia
 */
import * as THREE from "three";

// ---------- Materiales base ----------
const matRed    = new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.35, metalness: 0.1 });
const matBlue   = new THREE.MeshStandardMaterial({ color: 0x3b82f6, roughness: 0.22, metalness: 0.15 });
const matGreen  = new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.30, metalness: 0.05 });
const matPurple = new THREE.MeshStandardMaterial({ color: 0xa855f7, roughness: 0.28, metalness: 0.12 });
const matFloor  = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.9, metalness: 0.02 });

// Z-fighting pair materials
const matFightA = new THREE.MeshStandardMaterial({ color: 0xfbbf24, side: THREE.DoubleSide });
const matFightB = new THREE.MeshStandardMaterial({ color: 0xffffff, side: THREE.DoubleSide });

/**
 * Crea todo el contenido de la escena y lo devuelve empaquetado.
 */
export function createSceneObjects() {
  const group = new THREE.Group();

  // --- Objetos principales (superpuestos intencionalmente) ---
  const box = new THREE.Mesh(new THREE.BoxGeometry(2.4, 2.4, 2.4), matRed);
  box.position.set(0, 0.2, 0);
  box.name = "box";
  group.add(box);

  const sphere = new THREE.Mesh(new THREE.SphereGeometry(1.45, 40, 40), matBlue);
  sphere.position.set(1.6, 0.5, 0.9);
  sphere.name = "sphere";
  group.add(sphere);

  const cone = new THREE.Mesh(new THREE.ConeGeometry(1.1, 2.8, 32), matGreen);
  cone.position.set(-1.8, 0.4, 1.2);
  cone.name = "cone";
  group.add(cone);

  const torus = new THREE.Mesh(new THREE.TorusGeometry(1.0, 0.38, 20, 48), matPurple);
  torus.position.set(0.2, 1.8, -1.0);
  torus.rotation.x = Math.PI / 3;
  torus.name = "torus";
  group.add(torus);

  // --- Suelo ---
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(24, 24), matFloor);
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -1.0;
  floor.name = "floor";
  group.add(floor);

  // --- Planos de Z-fighting ---
  const zFightGroup = new THREE.Group();
  zFightGroup.name = "zfight-group";

  const planeA = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 2.8), matFightA);
  planeA.position.set(4.2, 1.0, -2.0);
  planeA.rotation.y = -0.3;
  planeA.name = "zfight-plane-a";
  zFightGroup.add(planeA);

  const planeB = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 2.8), matFightB);
  // Casi coplanar: separacion de 0.001 unidades → provoca Z-fighting
  planeB.position.set(4.2, 1.0, -1.999);
  planeB.rotation.y = -0.3;
  planeB.name = "zfight-plane-b";
  zFightGroup.add(planeB);

  group.add(zFightGroup);

  return {
    group,
    animatedObjects: [box, sphere, cone, torus],
    zFightGroup,
    planeA,
    planeB,
  };
}

/**
 * Crea luces de la escena.
 */
export function createLights() {
  const lights = new THREE.Group();

  const hemi = new THREE.HemisphereLight(0xc9ddf5, 0x1a1f2e, 0.75);
  lights.add(hemi);

  const dir = new THREE.DirectionalLight(0xffffff, 1.4);
  dir.position.set(5, 8, 4);
  dir.castShadow = false;
  lights.add(dir);

  const point = new THREE.PointLight(0x60a5fa, 0.6, 20);
  point.position.set(-3, 4, 2);
  lights.add(point);

  return lights;
}
