using UnityEngine;

/// <summary>
/// DepthTestToggle.cs
/// Permite activar/desactivar el depth testing en todos los materiales
/// de la escena para comparar el renderizado con y sin Z-buffer.
///
/// Controles:
///   Space = Toggle depth test ON/OFF
///
/// Adjuntar a cualquier GameObject de la escena.
/// </summary>
public class DepthTestToggle : MonoBehaviour
{
    [Header("Estado")]
    public bool depthTestEnabled = true;

    Renderer[] allRenderers;

    void Start()
    {
        allRenderers = FindObjectsByType<Renderer>(FindObjectsSortMode.None);
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            depthTestEnabled = !depthTestEnabled;
            ApplyDepthTest();
            Debug.Log($"[DepthTestToggle] Depth Test: {(depthTestEnabled ? "ON" : "OFF")}");
        }
    }

    void ApplyDepthTest()
    {
        // Refrescar lista por si se crearon objetos nuevos
        allRenderers = FindObjectsByType<Renderer>(FindObjectsSortMode.None);

        foreach (Renderer rend in allRenderers)
        {
            foreach (Material mat in rend.materials)
            {
                if (depthTestEnabled)
                {
                    // Restaurar depth test normal
                    mat.SetInt("_ZTest", (int)UnityEngine.Rendering.CompareFunction.LessEqual);
                    mat.SetInt("_ZWrite", 1);
                }
                else
                {
                    // Desactivar depth test: siempre pasar, no escribir
                    mat.SetInt("_ZTest", (int)UnityEngine.Rendering.CompareFunction.Always);
                    mat.SetInt("_ZWrite", 0);
                }
            }
        }
    }
}
