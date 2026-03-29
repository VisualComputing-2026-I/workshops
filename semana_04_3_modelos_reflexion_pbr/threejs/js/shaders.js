/**
 * shaders.js
 * Shaders GLSL para modelos de iluminacion: Lambert, Phong, Blinn-Phong.
 *
 * Ecuaciones implementadas:
 *  - Lambert (Diffuse): I_d = k_d * max(N . L, 0)
 *  - Phong (Specular):  I_s = k_s * max(R . V, 0)^shininess
 *  - Blinn-Phong:       I_s = k_s * max(N . H, 0)^shininess
 *
 * Donde:
 *  N = normal de superficie
 *  L = direccion hacia la luz
 *  V = direccion hacia la camara
 *  R = vector de reflexion = reflect(-L, N)
 *  H = half vector = normalize(L + V)
 */

// =============================================================================
// LAMBERT (Diffuse Only)
// =============================================================================
export const lambertVertexShader = /* glsl */ `
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vNormal = normalize(normalMatrix * normal);
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPos.xyz;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`;

export const lambertFragmentShader = /* glsl */ `
  uniform vec3 uLightPosition;
  uniform vec3 uLightColor;
  uniform vec3 uAmbientColor;
  uniform vec3 uDiffuseColor;
  uniform float uLightIntensity;

  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    // Direccion hacia la luz
    vec3 L = normalize(uLightPosition - vWorldPosition);
    vec3 N = normalize(vNormal);

    // Componente ambiente
    vec3 ambient = uAmbientColor * uDiffuseColor;

    // Componente difusa (Lambert): I_d = k_d * max(N . L, 0)
    float NdotL = max(dot(N, L), 0.0);
    vec3 diffuse = uLightColor * uDiffuseColor * NdotL * uLightIntensity;

    // Color final
    vec3 finalColor = ambient + diffuse;
    gl_FragColor = vec4(finalColor, 1.0);
  }
`;

// =============================================================================
// PHONG (Diffuse + Specular con vector de reflexion)
// =============================================================================
export const phongVertexShader = /* glsl */ `
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vNormal = normalize(normalMatrix * normal);
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPos.xyz;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`;

export const phongFragmentShader = /* glsl */ `
  uniform vec3 uLightPosition;
  uniform vec3 uLightColor;
  uniform vec3 uAmbientColor;
  uniform vec3 uDiffuseColor;
  uniform vec3 uSpecularColor;
  uniform float uShininess;
  uniform float uLightIntensity;
  uniform vec3 uCameraPosition;

  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(uLightPosition - vWorldPosition);
    vec3 V = normalize(uCameraPosition - vWorldPosition);

    // Componente ambiente
    vec3 ambient = uAmbientColor * uDiffuseColor;

    // Componente difusa (Lambert)
    float NdotL = max(dot(N, L), 0.0);
    vec3 diffuse = uLightColor * uDiffuseColor * NdotL * uLightIntensity;

    // Componente especular (Phong): I_s = k_s * max(R . V, 0)^shininess
    // R = reflect(-L, N) = 2 * (N . L) * N - L
    vec3 R = reflect(-L, N);
    float RdotV = max(dot(R, V), 0.0);
    float specularFactor = pow(RdotV, uShininess);
    vec3 specular = uLightColor * uSpecularColor * specularFactor * uLightIntensity;

    // Solo mostrar especular si hay luz difusa (evita highlights en superficies traseras)
    if (NdotL <= 0.0) {
      specular = vec3(0.0);
    }

    vec3 finalColor = ambient + diffuse + specular;
    gl_FragColor = vec4(finalColor, 1.0);
  }
`;

// =============================================================================
// BLINN-PHONG (Diffuse + Specular con half vector)
// =============================================================================
export const blinnPhongVertexShader = /* glsl */ `
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vNormal = normalize(normalMatrix * normal);
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPos.xyz;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`;

export const blinnPhongFragmentShader = /* glsl */ `
  uniform vec3 uLightPosition;
  uniform vec3 uLightColor;
  uniform vec3 uAmbientColor;
  uniform vec3 uDiffuseColor;
  uniform vec3 uSpecularColor;
  uniform float uShininess;
  uniform float uLightIntensity;
  uniform vec3 uCameraPosition;

  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(uLightPosition - vWorldPosition);
    vec3 V = normalize(uCameraPosition - vWorldPosition);

    // Componente ambiente
    vec3 ambient = uAmbientColor * uDiffuseColor;

    // Componente difusa (Lambert)
    float NdotL = max(dot(N, L), 0.0);
    vec3 diffuse = uLightColor * uDiffuseColor * NdotL * uLightIntensity;

    // Componente especular (Blinn-Phong): I_s = k_s * max(N . H, 0)^shininess
    // H = normalize(L + V) - half vector
    vec3 H = normalize(L + V);
    float NdotH = max(dot(N, H), 0.0);
    float specularFactor = pow(NdotH, uShininess);
    vec3 specular = uLightColor * uSpecularColor * specularFactor * uLightIntensity;

    if (NdotL <= 0.0) {
      specular = vec3(0.0);
    }

    vec3 finalColor = ambient + diffuse + specular;
    gl_FragColor = vec4(finalColor, 1.0);
  }
`;

// =============================================================================
// PBR SIMPLIFICADO (Cook-Torrance aproximado)
// =============================================================================
export const pbrVertexShader = /* glsl */ `
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vNormal = normalize(normalMatrix * normal);
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPos.xyz;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`;

export const pbrFragmentShader = /* glsl */ `
  #define PI 3.14159265359

  uniform vec3 uLightPosition;
  uniform vec3 uLightColor;
  uniform vec3 uAlbedo;
  uniform float uMetalness;
  uniform float uRoughness;
  uniform float uLightIntensity;
  uniform vec3 uCameraPosition;

  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  // Fresnel-Schlick approximation
  vec3 fresnelSchlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
  }

  // GGX Normal Distribution Function
  float distributionGGX(vec3 N, vec3 H, float roughness) {
    float a = roughness * roughness;
    float a2 = a * a;
    float NdotH = max(dot(N, H), 0.0);
    float NdotH2 = NdotH * NdotH;

    float num = a2;
    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;

    return num / denom;
  }

  // Schlick-GGX Geometry function
  float geometrySchlickGGX(float NdotV, float roughness) {
    float r = (roughness + 1.0);
    float k = (r * r) / 8.0;

    float num = NdotV;
    float denom = NdotV * (1.0 - k) + k;

    return num / denom;
  }

  // Smith's Geometry function
  float geometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    float ggx2 = geometrySchlickGGX(NdotV, roughness);
    float ggx1 = geometrySchlickGGX(NdotL, roughness);

    return ggx1 * ggx2;
  }

  void main() {
    vec3 N = normalize(vNormal);
    vec3 V = normalize(uCameraPosition - vWorldPosition);
    vec3 L = normalize(uLightPosition - vWorldPosition);
    vec3 H = normalize(V + L);

    // Calcular F0 (reflectancia en incidencia normal)
    // Dielectricos: ~0.04, Metales: usa el albedo
    vec3 F0 = vec3(0.04);
    F0 = mix(F0, uAlbedo, uMetalness);

    // Calcular radiance
    float distance = length(uLightPosition - vWorldPosition);
    float attenuation = 1.0 / (distance * distance);
    vec3 radiance = uLightColor * uLightIntensity * attenuation * 50.0;

    // Cook-Torrance BRDF
    float NDF = distributionGGX(N, H, uRoughness);
    float G = geometrySmith(N, V, L, uRoughness);
    vec3 F = fresnelSchlick(max(dot(H, V), 0.0), F0);

    // Specular
    vec3 numerator = NDF * G * F;
    float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001;
    vec3 specular = numerator / denominator;

    // kS = Fresnel, kD = 1 - kS (conservacion de energia)
    vec3 kS = F;
    vec3 kD = vec3(1.0) - kS;
    // Metales no tienen difuso
    kD *= 1.0 - uMetalness;

    // Lambert diffuse
    float NdotL = max(dot(N, L), 0.0);
    vec3 Lo = (kD * uAlbedo / PI + specular) * radiance * NdotL;

    // Ambiente simple
    vec3 ambient = vec3(0.03) * uAlbedo;
    vec3 color = ambient + Lo;

    // Tone mapping (Reinhard) y gamma correction
    color = color / (color + vec3(1.0));
    color = pow(color, vec3(1.0 / 2.2));

    gl_FragColor = vec4(color, 1.0);
  }
`;

// =============================================================================
// VISUALIZACION DE VECTORES (para debug)
// =============================================================================
export const vectorVisVertexShader = /* glsl */ `
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vNormal = normalize(normalMatrix * normal);
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPos.xyz;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`;

export const vectorVisFragmentShader = /* glsl */ `
  uniform vec3 uLightPosition;
  uniform vec3 uCameraPosition;
  uniform int uVectorMode; // 0: Normal, 1: Light dir, 2: View dir, 3: Reflect, 4: Half

  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(uLightPosition - vWorldPosition);
    vec3 V = normalize(uCameraPosition - vWorldPosition);
    vec3 R = reflect(-L, N);
    vec3 H = normalize(L + V);

    vec3 color;
    if (uVectorMode == 0) {
      // Visualizar normal (remap -1..1 a 0..1)
      color = N * 0.5 + 0.5;
    } else if (uVectorMode == 1) {
      // Visualizar direccion a la luz
      color = L * 0.5 + 0.5;
    } else if (uVectorMode == 2) {
      // Visualizar direccion a la camara
      color = V * 0.5 + 0.5;
    } else if (uVectorMode == 3) {
      // Visualizar vector de reflexion
      color = R * 0.5 + 0.5;
    } else {
      // Visualizar half vector
      color = H * 0.5 + 0.5;
    }

    gl_FragColor = vec4(color, 1.0);
  }
`;
