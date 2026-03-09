
# Taller - Etapas del Pipeline Programable



## Nombre de los estudiante 
Juan Esteban Santacruz Corredor
Nicolas Quezada Mora
Cristian Stiven Motta
Sebastian Andrade
Esteban Barrera 

## Descripcion breve

En este ejercicio se implementó un ShaderMaterial personalizado usando React Three Fiber (Three.js + React).

Se desarrollaron vertex y fragment shaders en GLSL que deforman una geometría mediante una animación basada en tiempo (uniform time) y generan colores a partir de coordenadas UV y normales.

## Implementaciones 

### Threjs
ShaderMaterial: Se utilizó ShaderMaterial dentro de React Three Fiber para definir vertex y fragment shaders personalizados.

Uniforms: Se pasaron uniforms desde React al shader:

- time → controla la animación del shader

- resolution → resolución de la pantalla

Vertex Shader: El vertex shader aplica una deformación tipo onda a los vértices de la geometría usando una función seno.

Fragment Shader: El fragment shader calcula el color usando:

- coordenadas UV

- orientación de la normal

Además se añadieron efectos de rim lighting y fresnel para resaltar los bordes de la geometría.


# Resultados visuales
### Threjs

![vis threjs](./media/threejs_3_4.gif)

La escena muestra un plano subdividido animado que se deforma continuamente mediante una onda.

El color del material cambia según las coordenadas UV y la orientación de las normales, generando un gradiente dinámico.

Los efectos de rim lighting y fresnel resaltan los bordes del objeto, dando una apariencia más estilizada.

# Codigo

### Threjs
Deformación en el vertex shader
```javascript
pos.z += sin(pos.x * 5.0 + time) * 0.1;
```
Cálculo de rim lighting

```javascript
float rim = 1.0 - max(dot(normal,vec3(0,0,1)),0.0);
```
Actualización del uniform time

```javascript
uniforms.time.value = clock.getElapsedTime()
```

# Prompts utilizados

### Threjs
"React Three Fiber shader material example"

"GLSL wave vertex deformation"

"GLSL rim lighting and fresnel effect"