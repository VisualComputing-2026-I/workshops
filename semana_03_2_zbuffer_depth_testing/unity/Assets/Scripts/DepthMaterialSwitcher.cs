using UnityEngine;

/// <summary>
/// DepthMaterialSwitcher.cs
/// Alterna entre materiales normales y el shader de profundidad
/// para visualizar el depth buffer de la escena.
///
/// Controles:
///   1 = Vista normal
///   2 = Depth no-lineal (nativo del GPU)
///   3 = Depth linealizado (near/far)
///   D = Toggle entre normal y depth
///
/// Adjuntar al mismo objeto que SceneSetup.
/// </summary>
[RequireComponent(typeof(SceneSetup))]
public class DepthMaterialSwitcher : MonoBehaviour
{
    [Header("Material de profundidad")]
    [Tooltip("Arrastrar aqui el material que usa el shader DepthVisualization")]
    public Material depthMaterial;

    enum ViewMode { Normal, Depth, DepthLinear }
    ViewMode currentMode = ViewMode.Normal;

    SceneSetup setup;
    Material[] originalMaterials;
    Renderer[] renderers;

    void Start()
    {
        setup = GetComponent<SceneSetup>();

        // Buscar todos los renderers de la escena
        renderers = FindObjectsByType<Renderer>(FindObjectsSortMode.None);
        originalMaterials = new Material[renderers.Length];
        for (int i = 0; i < renderers.Length; i++)
        {
            originalMaterials[i] = renderers[i].material;
        }

        // Si no se asigno material de profundidad, intentar crear uno
        if (depthMaterial == null)
        {
            Shader depthShader = Shader.Find("Custom/DepthVisualization");
            if (depthShader == null)
                depthShader = Shader.Find("Custom/DepthVisualizationURP");

            if (depthShader != null)
            {
                depthMaterial = new Material(depthShader);
            }
            else
            {
                Debug.LogWarning("DepthMaterialSwitcher: no se encontro shader de profundidad. " +
                    "Asegurate de que DepthVisualization.shader esta en Assets/Shaders/");
            }
        }
    }

    void Update()
    {
        // Teclas numericas para cambiar modo
        if (Input.GetKeyDown(KeyCode.Alpha1))
            SetMode(ViewMode.Normal);
        else if (Input.GetKeyDown(KeyCode.Alpha2))
            SetMode(ViewMode.Depth);
        else if (Input.GetKeyDown(KeyCode.Alpha3))
            SetMode(ViewMode.DepthLinear);
        else if (Input.GetKeyDown(KeyCode.D))
            ToggleDepth();
    }

    void ToggleDepth()
    {
        SetMode(currentMode == ViewMode.Normal ? ViewMode.Depth : ViewMode.Normal);
    }

    void SetMode(ViewMode mode)
    {
        currentMode = mode;

        for (int i = 0; i < renderers.Length; i++)
        {
            if (renderers[i] == null) continue;

            switch (mode)
            {
                case ViewMode.Normal:
                    renderers[i].material = originalMaterials[i];
                    break;

                case ViewMode.Depth:
                    if (depthMaterial != null)
                    {
                        Material m = new Material(depthMaterial);
                        m.DisableKeyword("_LINEARMODE_ON");
                        m.DisableKeyword("_LINEARMODE");
                        m.SetFloat("_LinearMode", 0f);
                        renderers[i].material = m;
                    }
                    break;

                case ViewMode.DepthLinear:
                    if (depthMaterial != null)
                    {
                        Material m = new Material(depthMaterial);
                        m.EnableKeyword("_LINEARMODE_ON");
                        m.EnableKeyword("_LINEARMODE");
                        m.SetFloat("_LinearMode", 1f);
                        renderers[i].material = m;
                    }
                    break;
            }
        }

        Debug.Log($"[DepthMaterialSwitcher] Modo: {mode}");
    }
}
