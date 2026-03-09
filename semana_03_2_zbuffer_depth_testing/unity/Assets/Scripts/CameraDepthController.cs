using UnityEngine;

/// <summary>
/// CameraDepthController.cs
/// Controla la camara para experimentar con el Z-buffer:
/// - Ajustar near/far clip planes en tiempo real
/// - Rotar la camara alrededor de la escena
/// - Teclado: Q/E para near, Z/X para far, R para reset
///
/// Adjuntar a la Main Camera.
/// </summary>
[RequireComponent(typeof(Camera))]
public class CameraDepthController : MonoBehaviour
{
    [Header("Rango de clip planes")]
    [Range(0.001f, 10f)]
    public float nearPlane = 0.1f;

    [Range(1f, 500f)]
    public float farPlane = 60f;

    [Header("Orbita")]
    public bool autoRotate = true;
    public float rotateSpeed = 12f;
    public Vector3 orbitTarget = new Vector3(0f, 0.6f, 0f);
    public float orbitDistance = 11f;
    public float orbitHeight = 4.5f;

    Camera cam;
    float orbitAngle;

    void Awake()
    {
        cam = GetComponent<Camera>();
    }

    void Update()
    {
        HandleInput();
        ApplyClipPlanes();

        if (autoRotate)
            Orbit();
    }

    void HandleInput()
    {
        float dt = Time.deltaTime;

        // Near plane: Q (bajar) / E (subir)
        if (Input.GetKey(KeyCode.Q)) nearPlane = Mathf.Max(0.001f, nearPlane - 0.5f * dt);
        if (Input.GetKey(KeyCode.E)) nearPlane = Mathf.Min(10f, nearPlane + 0.5f * dt);

        // Far plane: Z (bajar) / X (subir)
        if (Input.GetKey(KeyCode.Z)) farPlane = Mathf.Max(nearPlane + 0.5f, farPlane - 20f * dt);
        if (Input.GetKey(KeyCode.X)) farPlane = Mathf.Min(500f, farPlane + 20f * dt);

        // Reset: R
        if (Input.GetKeyDown(KeyCode.R))
        {
            nearPlane = 0.1f;
            farPlane = 60f;
        }

        // Toggle auto-rotacion: T
        if (Input.GetKeyDown(KeyCode.T))
            autoRotate = !autoRotate;
    }

    void ApplyClipPlanes()
    {
        cam.nearClipPlane = nearPlane;
        cam.farClipPlane = Mathf.Max(farPlane, nearPlane + 0.1f);
    }

    void Orbit()
    {
        orbitAngle += rotateSpeed * Time.deltaTime;
        float rad = orbitAngle * Mathf.Deg2Rad;
        Vector3 pos = orbitTarget + new Vector3(
            Mathf.Sin(rad) * orbitDistance,
            orbitHeight,
            Mathf.Cos(rad) * orbitDistance
        );
        transform.position = pos;
        transform.LookAt(orbitTarget);
    }
}
