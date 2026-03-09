using UnityEngine;

/// <summary>
/// ZFightingController.cs
/// Controla la demostracion de Z-fighting:
/// - Toggle visibilidad de los planos coplanares
/// - Resolver Z-fighting separando ligeramente los planos
/// - Teclas: F para mostrar/ocultar, G para resolver/provocar
///
/// Adjuntar al GameObject que tenga SceneSetup.
/// </summary>
[RequireComponent(typeof(SceneSetup))]
public class ZFightingController : MonoBehaviour
{
    [Header("Z-Fighting")]
    [Tooltip("Mostrar los planos de Z-fighting")]
    public bool showZFighting = true;

    [Tooltip("Resolver Z-fighting (separar planos)")]
    public bool solveZFighting = false;

    [Header("Parametros de solucion")]
    [Tooltip("Separacion en Z cuando se resuelve")]
    public float solvedOffset = 0.05f;

    SceneSetup setup;
    float originalOffset;

    void Awake()
    {
        setup = GetComponent<SceneSetup>();
    }

    void Start()
    {
        if (setup.planeB != null)
            originalOffset = setup.planeB.transform.localPosition.z;
    }

    void Update()
    {
        // Toggle visibilidad: F
        if (Input.GetKeyDown(KeyCode.F))
            showZFighting = !showZFighting;

        // Toggle solucion: G
        if (Input.GetKeyDown(KeyCode.G))
            solveZFighting = !solveZFighting;

        ApplyState();
    }

    void ApplyState()
    {
        if (setup.zFightingParent != null)
            setup.zFightingParent.SetActive(showZFighting);

        if (setup.planeB != null)
        {
            Vector3 pos = setup.planeB.transform.localPosition;
            pos.z = solveZFighting ? solvedOffset : originalOffset;
            setup.planeB.transform.localPosition = pos;
        }
    }
}
