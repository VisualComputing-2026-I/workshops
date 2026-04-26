using UnityEngine;

public class MainScript : MonoBehaviour
{
    [Header("Referencias (Autogeneradas)")]
    private Transform player;
    private Transform cameraTransform;
    private Transform targetCube;
    
    [Header("Configuracion")]
    public float moveSpeed = 5f;
    public float turnSpeed = 5f; // Usado para la cámara como sugeriste
    
    private string actionState = "Esperando interaccion...";

    void Start()
    {
        // 1. Piso
        GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
        floor.name = "Floor";
        floor.transform.localScale = new Vector3(5, 1, 5);
        if (floor.GetComponent<Renderer>() != null) floor.GetComponent<Renderer>().material.color = new Color(0.2f, 0.4f, 0.3f);
        
        // 2. Cubo Interactivo
        GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cube.name = "TargetCube";
        cube.transform.position = new Vector3(0, 0.5f, 3);
        if (cube.GetComponent<Renderer>() != null) cube.GetComponent<Renderer>().material.color = Color.red;
        targetCube = cube.transform;
        
        // 3. Jugador
        GameObject pObj = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        pObj.name = "Player";
        pObj.transform.position = new Vector3(0, 1f, 0);
        if (pObj.GetComponent<Renderer>() != null) pObj.GetComponent<Renderer>().material.color = Color.blue;
        player = pObj.transform;
        
        // 4. Configurar Cámara (Como Orbit Rig)
        Camera cam = Camera.main;
        if (cam == null) 
        {
            GameObject camObj = new GameObject("Main Camera");
            camObj.tag = "MainCamera";
            cam = camObj.AddComponent<Camera>();
        }
        
        // Desanclamos temporalmente la cámara para que RotateAround funcione libremente en LateUpdate
        cam.transform.SetParent(null); 
        cameraTransform = cam.transform;

        // Posicionar la cámara detrás y arriba del jugador, mirando hacia él
        cameraTransform.position = player.position + new Vector3(0, 2f, -5f);
        cameraTransform.LookAt(player.position);
    }

    void Update()
    {
        if (player == null || cameraTransform == null) return;

        HandleMovement();
        HandleClick();
    }

    // Aquí implementamos tu sugerencia exacta, con dos mejoras importantes:
    // 1. Usamos GetMouseButton(1) (Click derecho mantenido) en lugar de GetMouseDown(0) (Pulsado solo una vez) para que puedas sostener y mover continuamente sin bloquear tu click izquierdo para UI.
    // 2. Movemos la cámara también junto al jugador cuando este camina (HandleMovement se ocupa de esto).
    void LateUpdate() 
    {
        if (player == null || cameraTransform == null) return;

        // Si mantenemos oprimido el Click Derecho, hacemos el Orbit (RotateAround)
        if(Input.GetMouseButton(1))
        {
            float deltaX = Input.GetAxis("Mouse X") * turnSpeed;
            float deltaY = Input.GetAxis("Mouse Y") * turnSpeed; // Bonus: también arriba/abajo
            
            // Sugerencia aplicada:
            cameraTransform.RotateAround(player.position, Vector3.up, deltaX);
            
            // Orbitar arriba/abajo basado en la derecha de la cámara actual
            cameraTransform.RotateAround(player.position, cameraTransform.right, -deltaY);
            
            // Bloquea el eje Z de rotación forzando a la cámara a mirar siempre bien centrada al jugador
            cameraTransform.LookAt(player.position);
        }
    }

    private void HandleMovement()
    {
        // Mover el jugador leyendo directo las teclas físicas para evitar bugs de Input Manager
        float h = 0f;
        float v = 0f;

        if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow)) v += 1f;
        if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow)) v -= 1f;
        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) h += 1f;
        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) h -= 1f;
        
        // Calcular que "Hacia adelante" sea visualmente hacia donde apunta la cámara (Cámara 3ra persona)
        Vector3 forward = cameraTransform.forward;
        Vector3 right = cameraTransform.right;
        
        // Remover el componente Y para no "volar" si miras arriba/abajo
        forward.y = 0f;
        right.y = 0f;
        forward.Normalize();
        right.Normalize();

        Vector3 moveDir = (right * h + forward * v).normalized;

        if (moveDir.magnitude > 0.1f)
        {
            // Movemos al jugador físicamente
            player.position += moveDir * moveSpeed * Time.deltaTime;

            // Arrastramos la cámara con el jugador en este mismo frame
            cameraTransform.position += moveDir * moveSpeed * Time.deltaTime;
        }
    }

    private void HandleClick()
    {
        // Click en el objeto rojo usando Click Izquierdo
        if (Input.GetMouseButtonDown(0))
        {
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            if (Physics.Raycast(ray, out RaycastHit hit))
            {
                if (hit.transform == targetCube)
                {
                    actionState = "Cubo interaccionado!!";
                    targetCube.GetComponent<Renderer>().material.color = new Color(Random.value, Random.value, Random.value);
                    targetCube.localScale = Vector3.one * Random.Range(0.5f, 1.5f);
                }
            }
        }
    }

    private void OnGUI()
    {
        GUILayout.BeginArea(new Rect(15, 15, 310, 320), GUI.skin.box);
        GUILayout.Label("TALLER 6.1: RotateAround Camera (Orbit Rig)");
        GUILayout.Space(5);
        GUILayout.Label("Controles (3ra Persona):");
        GUILayout.Label("- Mover: W A S D o Flechas");
        GUILayout.Label("- Orbitar Camara: Oprime CLICK DERECHO");
        GUILayout.Label("- Interactuar: Click izquierdo en cubo rojo");
        GUILayout.Space(5);
        
        if (player != null)
            GUILayout.Label($"Pos. Jugador: ({player.position.x:F1}, {player.position.y:F1}, {player.position.z:F1})");
        GUILayout.Label($"Estado: {actionState}");
        
        GUILayout.Space(15);
        GUILayout.Label($"Velocidad Movement: {moveSpeed:F1}");
        moveSpeed = GUILayout.HorizontalSlider(moveSpeed, 1f, 15f);
        
        GUILayout.Label($"Velocidad de Turn Mouse {turnSpeed:F1}");
        turnSpeed = GUILayout.HorizontalSlider(turnSpeed, 1f, 15f);

        GUILayout.Space(15);
        if (GUILayout.Button("Resetear Jugador (Test de UI)", GUILayout.Height(35)))
        {
            if (player != null)
            {
                player.position = new Vector3(0, 1f, 0);
                if (cameraTransform != null)
                {
                    cameraTransform.position = player.position + new Vector3(0, 2f, -5f);
                    cameraTransform.LookAt(player.position);
                }
                actionState = "Rotacion/Posicion reseteada";
            }
        }
        GUILayout.EndArea();
    }
}