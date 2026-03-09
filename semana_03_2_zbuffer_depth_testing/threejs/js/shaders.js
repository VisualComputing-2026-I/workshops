/**
 * shaders.js
 * Shaders GLSL personalizados para visualizacion de profundidad.
 *
 * - depthVisualization: muestra gl_FragCoord.z mapeado a escala de grises
 *   (tal como pide el taller: gl_FragColor = vec4(vec3(gl_FragCoord.z), 1.0))
 *
 * - linearDepthVisualization: lineariza la profundidad usando near/far
 *   para comparar con el depth buffer no-lineal por defecto
 */

// ---------- Depth no-lineal (nativo de WebGL) ----------
export const depthVertexShader = /* glsl */ `
  void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

export const depthFragmentShader = /* glsl */ `
  void main() {
    // Profundidad tal como la guarda el GPU (no lineal)
    gl_FragColor = vec4(vec3(gl_FragCoord.z), 1.0);
  }
`;

// ---------- Depth linealizado ----------
export const linearDepthVertexShader = /* glsl */ `
  varying float vViewZ;
  void main() {
    vec4 viewPos = modelViewMatrix * vec4(position, 1.0);
    vViewZ = -viewPos.z;  // distancia positiva desde la camara
    gl_Position = projectionMatrix * viewPos;
  }
`;

export const linearDepthFragmentShader = /* glsl */ `
  uniform float uNear;
  uniform float uFar;
  varying float vViewZ;
  void main() {
    // Mapear distancia al rango [0,1] linealmente
    float linearDepth = (vViewZ - uNear) / (uFar - uNear);
    linearDepth = clamp(linearDepth, 0.0, 1.0);
    gl_FragColor = vec4(vec3(linearDepth), 1.0);
  }
`;
