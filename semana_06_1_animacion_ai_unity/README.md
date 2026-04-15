# Taller — Animación con IA en Unity para Personajes Autónomos

**Nombre del estudiante:**

- Esteban Barrera Sanabria
- Cristian Steven Motta Ojeda
- Juan Esteban Santacruz Corredor
- Sebastian Andrade Cedano
- Nicolas Quezada Mora
- Jeronimo Bermudez

**Fecha de entrega:** 15 de abril de 2026

---

## Descripción

El objetivo del taller es desarrollar comportamientos autónomos para NPCs en Unity utilizando NavMesh y una máquina de estados finitos (FSM) con control dinámico de animaciones.

Para esto, se implementó un agente (Husky) que patrulla entre waypoints distribuidos en una escena con obstáculos, detecta al jugador por distancia y lo persigue, sincronizando en todo momento las animaciones de Idle, Walk y Run con la velocidad real del NavMeshAgent.

**Entorno utilizado:**

- Unity 6.3 LTS
- NavMeshAgent / NavMeshSurface / NavMeshObstacle
- Animator Controller
- Quaternius para el Modelo 3D animado (Husky)

---

## Implementaciones

### NavMesh para navegación

Se configuró el NavMesh utilizando el paquete AI Navigation de Unity. Primero, el suelo recibió el componente `NavMesh Surface` y se ejecutó el Bake directamente desde el Inspector. Los obstáculos distribuidos en la escena recibieron el componente `NavMesh Obstacle` con la opción `Carve` activada, lo que permite al agente evitarlos dinámicamente sin necesidad de recalcular el bake.

Finlalmente se colocaron 4 waypoints como GameObjects vacíos formando un cuadrado alrededor de los obstáculos, con coordenadas sobre el área navegable.

### Máquina de Estados Finitos FSM

Se implementó una FSM con tres estados usando un `enum` en C# y un `switch` en `Update`:

1. **Idle**: el NPC permanece detenido durante 2 segundos con `agent.isStopped = true`, acumulando tiempo con `Time.deltaTime`. Al cumplirse el timer transiciona a Patrol.
2. **Patrol**: el agente recorre los 4 waypoints en orden cíclico usando `agent.SetDestination()` a velocidad de 2 unidades/s. Se implementó un flag `waitingForPath` para evitar que `remainingDistance` se evalúe antes de que el nuevo path esté calculado, lo que causaba que el agente ciclara entre los primeros dos waypoints. Si el jugador entra al radio de detección (< 10 m), transiciona a Chase.
3. **Chase**: el agente actualiza su destino al jugador cada frame a velocidad de 5 unidades/s, activando la animación Run. Si la distancia supera 15 m, regresa a Patrol.

Las transiciones están basadas exclusivamente en distancia calculada con `Vector3.Distance()`.

### Control de Animaciones

Se creó un Animator Controller con tres estados: Idle, Walk y Run, cada uno con su clip de animación asignado. Un parámetro Float llamado `Speed` controla las transiciones. El valor se actualiza cada frame con `agent.velocity.magnitude`, que refleja la velocidad real del agente y no la configurada, permitiendo detectar deceleraciones y bloqueos. Se desactivó `Has Exit Time` en todas las transiciones para lograr respuesta inmediata. Se desactivó `Apply Root Motion` en el componente Animator para evitar conflictos entre la animación y el NavMeshAgent.

Este seria el mapa completo de transiciones aplicadas

- Idle → Walk: Speed > 0.1
- Walk → Run: Speed > 4.5
- Run → Walk: Speed < 4.0
- Walk → Idle: Speed < 0.1

### Detección de Jugador

La detección se implementa por distancia en cada frame del `Update`. Se usaron dos radios configurables desde el Inspector: `detectionRadius` (10 m) para iniciar la persecución y `loseRadius` (15 m) para volver a patrullar. Los radios se visualizan en el editor con `OnDrawGizmosSelected()` usando esferas de alambre en amarillo y rojo respectivamente.

---

## Resultados Visuales

### Vista general de la FSM en funcionamiento

![Demo completa](media/husky.gif)

---

## Código Relevante

**Máquina de estados con enum y switch:**

```csharp
void Update()
{
    switch (currentState)
    {
        case AIState.Idle:   HandleIdle();   break;
        case AIState.Patrol: HandlePatrol(); break;
        case AIState.Chase:  HandleChase();  break;
    }

    animator.SetFloat("Speed", agent.velocity.magnitude);
}
```

**Transición Idle → Patrol:**

```csharp
void HandleIdle()
{
    agent.isStopped = true;
    idleTimer += Time.deltaTime;
    if (idleTimer >= 2f)
    {
        idleTimer = 0f;
        agent.isStopped = false;
        currentState = AIState.Patrol;
        SetWaypoint(0);
        Debug.Log("IDLE → PATROL");
    }
}
```

**Patrullaje con flag waitingForPath para evitar saltos de waypoint:**

```csharp
void HandlePatrol()
{
    agent.speed = patrolSpeed;

    if (waitingForPath)
    {
        if (agent.pathPending) return;
        waitingForPath = false;
    }

    if (agent.hasPath && agent.remainingDistance <= 0.5f)
    {
        int next = (currentWaypointIndex + 1) % waypoints.Length;
        SetWaypoint(next);
    }

    if (PlayerDetected())
        currentState = AIState.Chase;
}
```

**Persecución y detección por distancia:**

```csharp
void HandleChase()
{
    agent.speed = chaseSpeed;
    agent.SetDestination(player.position);
    if (PlayerLost()) currentState = AIState.Patrol;
}

bool PlayerDetected() =>
    Vector3.Distance(transform.position, player.position) < detectionRadius;

bool PlayerLost() =>
    Vector3.Distance(transform.position, player.position) > loseRadius;
```

---

## Prompts Utilizados

1. Diagnosticar el bug de ciclado entre WP_0 y WP_1, la causa era la incongurencia de localización de los otros dos Waypoints, debian estar incluidos en el mismo plano (Y = 0)
2. Identificar el conflicto entre `Apply Root Motion` del Animator y el NavMeshAgent, que hacía que el agente se quedara quieto aunque el path se calculara correctamente.

---

## Aprendizajes y Dificultades

### Aprendizajes

- `agent.velocity.magnitude` es la fuente más confiable para sincronizar animaciones porque refleja la velocidad real del agente, no la configurada, lo que permite detectar cuando el agente desacelera en curvas o está momentáneamente bloqueado.
- **Apply Root Motion** debe desactivarse siempre que se use NavMeshAgent. Cuando está activo, la animación intenta mover el transform del personaje en conflicto directo con el agente, resultando en que el personaje se queda estático aunque el path esté activo.
- El flag `waitingForPath` es un patrón necesario para patrullajes cíclicos: sin él, `remainingDistance` reporta 0 durante el frame de transición entre destinos, haciendo que la condición de llegada se dispare múltiples veces seguidas y saltando waypoints.

### Dificultades

- El bug más difícil de diagnosticar fue el ciclado entre WP_0 y WP_1, ya ezplicado anteriormente.
- Las animaciones de modelos importados pueden tener `Apply Root Motion` activo por defecto, lo que es correcto para personajes controlados por el jugador pero incorrecto para agentes con NavMeshAgent.
