using UnityEngine;

/// <summary>
/// Controlador de UI para ajustar parametros de iluminacion en tiempo real.
/// Muestra un panel con sliders para shininess, colores, y parametros PBR.
/// </summary>
public class IlluminationUI : MonoBehaviour
{
    [Header("References")]
    public ReflectionModelsSetup sceneSetup;

    [Header("Light Animation")]
    public bool animateLight = true;
    public float lightRotationSpeed = 30f;
    public float lightOrbitRadius = 8f;
    public float lightHeight = 6f;

    // Parametros actuales
    private float shininess = 32f;
    private float metalness = 0f;
    private float roughness = 0.4f;
    private Color diffuseColor = new Color(0.8f, 0.2f, 0.2f);
    private Color specularColor = Color.white;

    // UI State
    private bool showUI = true;
    private Rect windowRect = new Rect(20, 20, 300, 400);

    // Presets
    private string[] presetNames = {
        "Plastico Rojo",
        "Plastico Azul",
        "Metal Dorado",
        "Metal Cromado",
        "Goma Mate",
        "Ceramica"
    };

    void Start()
    {
        if (sceneSetup == null)
        {
            sceneSetup = FindObjectOfType<ReflectionModelsSetup>();
        }
    }

    void Update()
    {
        // Toggle UI con H
        if (Input.GetKeyDown(KeyCode.H))
        {
            showUI = !showUI;
        }

        // Animar luz
        if (animateLight && sceneSetup != null && sceneSetup.mainLight != null)
        {
            float angle = Time.time * lightRotationSpeed;
            Vector3 lightPos = new Vector3(
                Mathf.Sin(angle * Mathf.Deg2Rad) * lightOrbitRadius,
                lightHeight,
                Mathf.Cos(angle * Mathf.Deg2Rad) * lightOrbitRadius
            );

            sceneSetup.mainLight.transform.position = lightPos;
            sceneSetup.mainLight.transform.LookAt(Vector3.zero);
        }
    }

    void OnGUI()
    {
        if (!showUI) return;

        // Aplicar un estilo mas legible
        GUI.skin.label.fontSize = 12;
        GUI.skin.button.fontSize = 12;
        GUI.skin.horizontalSlider.fixedHeight = 15;

        windowRect = GUILayout.Window(0, windowRect, DrawWindow, "Modelos de Iluminacion");
    }

    void DrawWindow(int windowID)
    {
        GUILayout.Space(10);

        // === Seccion: Shininess ===
        GUILayout.Label($"Shininess: {shininess:F0}");
        float newShininess = GUILayout.HorizontalSlider(shininess, 1f, 256f);
        if (newShininess != shininess)
        {
            shininess = newShininess;
            sceneSetup?.SetShininess(shininess);
        }

        GUILayout.Space(15);

        // === Seccion: PBR ===
        GUILayout.Label("--- PBR Parameters ---");

        GUILayout.Label($"Metalness: {metalness:F2}");
        float newMetalness = GUILayout.HorizontalSlider(metalness, 0f, 1f);
        if (newMetalness != metalness)
        {
            metalness = newMetalness;
            sceneSetup?.SetPBRMetalness(metalness);
        }

        GUILayout.Label($"Roughness: {roughness:F2}");
        float newRoughness = GUILayout.HorizontalSlider(roughness, 0f, 1f);
        if (newRoughness != roughness)
        {
            roughness = newRoughness;
            sceneSetup?.SetPBRRoughness(roughness);
        }

        GUILayout.Space(15);

        // === Seccion: Luz ===
        GUILayout.Label("--- Luz ---");
        animateLight = GUILayout.Toggle(animateLight, "Animar luz");

        GUILayout.Label($"Velocidad: {lightRotationSpeed:F0}");
        lightRotationSpeed = GUILayout.HorizontalSlider(lightRotationSpeed, 5f, 120f);

        GUILayout.Space(15);

        // === Seccion: Presets ===
        GUILayout.Label("--- Presets ---");
        GUILayout.BeginHorizontal();
        int buttonsPerRow = 2;
        for (int i = 0; i < presetNames.Length; i++)
        {
            if (i > 0 && i % buttonsPerRow == 0)
            {
                GUILayout.EndHorizontal();
                GUILayout.BeginHorizontal();
            }

            if (GUILayout.Button(presetNames[i]))
            {
                ApplyPreset(i);
            }
        }
        GUILayout.EndHorizontal();

        GUILayout.Space(15);

        // === Info ===
        GUILayout.Label("Controles:", EditorStyles());
        GUILayout.Label("  H - Mostrar/ocultar UI", SmallStyle());
        GUILayout.Label("  Click + Arrastrar - Rotar camara", SmallStyle());

        // Hacer ventana arrastrable
        GUI.DragWindow();
    }

    void ApplyPreset(int index)
    {
        switch (index)
        {
            case 0: // Plastico Rojo
                diffuseColor = new Color(0.8f, 0.16f, 0.21f);
                specularColor = Color.white;
                shininess = 32f;
                metalness = 0f;
                roughness = 0.4f;
                break;

            case 1: // Plastico Azul
                diffuseColor = new Color(0.12f, 0.38f, 0.57f);
                specularColor = Color.white;
                shininess = 48f;
                metalness = 0f;
                roughness = 0.35f;
                break;

            case 2: // Metal Dorado
                diffuseColor = new Color(0.83f, 0.66f, 0.33f);
                specularColor = new Color(1f, 0.92f, 0.65f);
                shininess = 100f;
                metalness = 1f;
                roughness = 0.3f;
                break;

            case 3: // Metal Cromado
                diffuseColor = new Color(0.63f, 0.63f, 0.63f);
                specularColor = Color.white;
                shininess = 200f;
                metalness = 1f;
                roughness = 0.1f;
                break;

            case 4: // Goma Mate
                diffuseColor = new Color(0.18f, 0.2f, 0.21f);
                specularColor = new Color(0.18f, 0.2f, 0.21f);
                shininess = 5f;
                metalness = 0f;
                roughness = 0.95f;
                break;

            case 5: // Ceramica
                diffuseColor = new Color(0.96f, 0.94f, 0.9f);
                specularColor = Color.white;
                shininess = 60f;
                metalness = 0f;
                roughness = 0.5f;
                break;
        }

        // Aplicar cambios
        sceneSetup?.SetDiffuseColor(diffuseColor);
        sceneSetup?.SetSpecularColor(specularColor);
        sceneSetup?.SetShininess(shininess);
        sceneSetup?.SetPBRMetalness(metalness);
        sceneSetup?.SetPBRRoughness(roughness);
    }

    GUIStyle EditorStyles()
    {
        GUIStyle style = new GUIStyle(GUI.skin.label);
        style.fontStyle = FontStyle.Bold;
        style.fontSize = 11;
        return style;
    }

    GUIStyle SmallStyle()
    {
        GUIStyle style = new GUIStyle(GUI.skin.label);
        style.fontSize = 10;
        style.normal.textColor = Color.gray;
        return style;
    }
}
