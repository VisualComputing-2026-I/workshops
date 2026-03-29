using UnityEngine;

/// <summary>
/// HUD que muestra informacion sobre los modelos de iluminacion.
/// Muestra las ecuaciones matematicas de cada modelo.
/// </summary>
public class IlluminationHUD : MonoBehaviour
{
    [Header("Display Settings")]
    public bool showEquations = true;
    public bool showLegend = true;

    private GUIStyle titleStyle;
    private GUIStyle equationStyle;
    private GUIStyle labelStyle;

    private string[] modelNames = { "Lambert", "Phong", "Blinn-Phong", "PBR" };

    private string[] equations = {
        "I = Ia + Id\nId = kd * max(N . L, 0)",
        "I = Ia + Id + Is\nIs = ks * max(R . V, 0)^n\nR = 2(N . L)N - L",
        "I = Ia + Id + Is\nIs = ks * max(N . H, 0)^n\nH = normalize(L + V)",
        "fr = kd * (c/pi) + (D*F*G) / (4*(N.V)*(N.L))\nD = GGX, F = Fresnel, G = Smith"
    };

    void Start()
    {
        InitStyles();
    }

    void InitStyles()
    {
        titleStyle = new GUIStyle();
        titleStyle.fontSize = 16;
        titleStyle.fontStyle = FontStyle.Bold;
        titleStyle.normal.textColor = Color.white;

        equationStyle = new GUIStyle();
        equationStyle.fontSize = 11;
        equationStyle.normal.textColor = new Color(0.6f, 0.8f, 1f);
        equationStyle.padding = new RectOffset(10, 10, 5, 5);

        labelStyle = new GUIStyle();
        labelStyle.fontSize = 12;
        labelStyle.normal.textColor = Color.white;
    }

    void OnGUI()
    {
        if (titleStyle == null) InitStyles();

        // Panel de ecuaciones (esquina inferior izquierda)
        if (showEquations)
        {
            DrawEquationsPanel();
        }

        // Leyenda de colores (esquina inferior derecha)
        if (showLegend)
        {
            DrawLegend();
        }
    }

    void DrawEquationsPanel()
    {
        float panelWidth = 320;
        float panelHeight = 200;
        float x = 20;
        float y = Screen.height - panelHeight - 20;

        // Fondo semi-transparente
        GUI.Box(new Rect(x - 10, y - 10, panelWidth, panelHeight), "");

        GUILayout.BeginArea(new Rect(x, y, panelWidth - 20, panelHeight - 20));

        GUILayout.Label("Ecuaciones de Iluminacion", titleStyle);
        GUILayout.Space(10);

        for (int i = 0; i < modelNames.Length; i++)
        {
            GUILayout.BeginHorizontal();

            // Color del modelo
            Color[] colors = {
                new Color(0.94f, 0.27f, 0.27f), // Rojo
                new Color(0.98f, 0.45f, 0.14f), // Naranja
                new Color(0.92f, 0.7f, 0.05f),  // Amarillo
                new Color(0.13f, 0.77f, 0.37f)  // Verde
            };

            GUIStyle colorBox = new GUIStyle();
            colorBox.normal.background = MakeTexture(2, 2, colors[i]);

            GUILayout.Box("", colorBox, GUILayout.Width(12), GUILayout.Height(12));
            GUILayout.Space(5);
            GUILayout.Label(modelNames[i] + ":", labelStyle);

            GUILayout.EndHorizontal();
        }

        GUILayout.EndArea();
    }

    void DrawLegend()
    {
        float panelWidth = 280;
        float panelHeight = 120;
        float x = Screen.width - panelWidth - 20;
        float y = Screen.height - panelHeight - 20;

        GUI.Box(new Rect(x - 10, y - 10, panelWidth, panelHeight), "");

        GUILayout.BeginArea(new Rect(x, y, panelWidth - 20, panelHeight - 20));

        GUILayout.Label("PBR Parameters", titleStyle);
        GUILayout.Space(5);

        GUILayout.Label("Metalness: 0 = Dielectrico, 1 = Metal", labelStyle);
        GUILayout.Label("Roughness: 0 = Espejo, 1 = Mate", labelStyle);
        GUILayout.Space(5);
        GUILayout.Label("D (NDF): GGX Distribution", labelStyle);
        GUILayout.Label("F (Fresnel): Schlick Approximation", labelStyle);
        GUILayout.Label("G (Geometry): Smith's Method", labelStyle);

        GUILayout.EndArea();
    }

    Texture2D MakeTexture(int width, int height, Color color)
    {
        Color[] pixels = new Color[width * height];
        for (int i = 0; i < pixels.Length; i++)
        {
            pixels[i] = color;
        }

        Texture2D texture = new Texture2D(width, height);
        texture.SetPixels(pixels);
        texture.Apply();
        return texture;
    }
}
