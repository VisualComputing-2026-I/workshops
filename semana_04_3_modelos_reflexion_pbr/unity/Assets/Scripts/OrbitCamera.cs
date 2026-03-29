using UnityEngine;

/// <summary>
/// Controlador de camara orbital simple para inspeccionar la escena.
/// Permite rotar, hacer zoom y panear con el mouse.
/// </summary>
public class OrbitCamera : MonoBehaviour
{
    [Header("Target")]
    public Transform target;
    public Vector3 targetOffset = Vector3.zero;

    [Header("Orbit Settings")]
    public float distance = 12f;
    public float minDistance = 3f;
    public float maxDistance = 30f;

    [Header("Rotation")]
    public float rotationSensitivity = 3f;
    public float yMinLimit = -20f;
    public float yMaxLimit = 80f;

    [Header("Zoom")]
    public float zoomSensitivity = 5f;
    public float zoomSmoothing = 5f;

    [Header("Auto Rotate")]
    public bool autoRotate = false;
    public float autoRotateSpeed = 10f;

    // Estado interno
    private float currentX = 0f;
    private float currentY = 30f;
    private float targetDistance;
    private Vector3 targetPosition;

    void Start()
    {
        targetDistance = distance;

        // Calcular angulos iniciales desde la posicion actual
        if (target != null)
        {
            Vector3 direction = transform.position - target.position;
            currentX = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;
            currentY = Mathf.Asin(direction.y / direction.magnitude) * Mathf.Rad2Deg;
        }

        targetPosition = target != null ? target.position : Vector3.zero;
    }

    void LateUpdate()
    {
        if (target == null)
        {
            targetPosition = targetOffset;
        }
        else
        {
            targetPosition = target.position + targetOffset;
        }

        HandleInput();
        UpdateCameraPosition();
    }

    void HandleInput()
    {
        // Auto rotacion
        if (autoRotate && !Input.GetMouseButton(0) && !Input.GetMouseButton(1))
        {
            currentX += autoRotateSpeed * Time.deltaTime;
        }

        // Rotacion con click izquierdo
        if (Input.GetMouseButton(0))
        {
            currentX += Input.GetAxis("Mouse X") * rotationSensitivity;
            currentY -= Input.GetAxis("Mouse Y") * rotationSensitivity;
            currentY = Mathf.Clamp(currentY, yMinLimit, yMaxLimit);
        }

        // Zoom con scroll
        float scroll = Input.GetAxis("Mouse ScrollWheel");
        if (Mathf.Abs(scroll) > 0.01f)
        {
            targetDistance -= scroll * zoomSensitivity;
            targetDistance = Mathf.Clamp(targetDistance, minDistance, maxDistance);
        }

        // Suavizar zoom
        distance = Mathf.Lerp(distance, targetDistance, Time.deltaTime * zoomSmoothing);
    }

    void UpdateCameraPosition()
    {
        // Calcular posicion en coordenadas esfericas
        Quaternion rotation = Quaternion.Euler(currentY, currentX, 0);
        Vector3 position = rotation * new Vector3(0, 0, -distance) + targetPosition;

        transform.position = position;
        transform.LookAt(targetPosition);
    }

    // API publica
    public void SetAutoRotate(bool value)
    {
        autoRotate = value;
    }

    public void SetTarget(Transform newTarget)
    {
        target = newTarget;
    }

    public void ResetView()
    {
        currentX = 0f;
        currentY = 30f;
        targetDistance = 12f;
    }
}
