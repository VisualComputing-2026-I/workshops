using UnityEngine;

/// <summary>
/// HUDOverlay.cs
/// Muestra un HUD en pantalla con el estado actual de los controles
/// del taller Z-Buffer: near/far planes, modo de vista, Z-fighting, etc.
///
/// Adjuntar a cualquier GameObject de la escena.
/// </summary>
public class HUDOverlay : MonoBehaviour
{
    CameraDepthController camController;
    DepthTestToggle depthToggle;
    ZFightingController zfController;

    GUIStyle boxStyle;
    GUIStyle labelStyle;
    GUIStyle headerStyle;

    void Start()
    {
        camController = FindFirstObjectByType<CameraDepthController>();
        depthToggle = FindFirstObjectByType<DepthTestToggle>();
        zfController = FindFirstObjectByType<ZFightingController>();
    }

    void OnGUI()
    {
        InitStyles();

        float w = 320f;
        float h = 280f;
        Rect area = new Rect(12, 12, w, h);

        GUI.Box(area, "", boxStyle);

        GUILayout.BeginArea(new Rect(area.x + 12, area.y + 10, w - 24, h - 20));

        GUILayout.Label("Taller Z-Buffer & Depth Testing", headerStyle);
        GUILayout.Space(6);

        if (camController != null)
        {
            GUILayout.Label($"Near Plane: {camController.nearPlane:F3}  (Q / E)", labelStyle);
            GUILayout.Label($"Far Plane:  {camController.farPlane:F1}  (Z / X)", labelStyle);
            GUILayout.Label($"Auto-rotar: {(camController.autoRotate ? "ON" : "OFF")}  (T)", labelStyle);
        }

        GUILayout.Space(4);

        if (depthToggle != null)
        {
            string depthState = depthToggle.depthTestEnabled ? "ON" : "OFF";
            GUILayout.Label($"Depth Test: {depthState}  (Space)", labelStyle);
        }

        GUILayout.Space(4);

        GUILayout.Label("Vista: 1=Normal  2=Depth  3=Lineal  D=Toggle", labelStyle);

        GUILayout.Space(4);

        if (zfController != null)
        {
            string zfShow = zfController.showZFighting ? "Visible" : "Oculto";
            string zfSolve = zfController.solveZFighting ? "Resuelto" : "Activo";
            GUILayout.Label($"Z-Fighting: {zfShow} (F)  |  {zfSolve} (G)", labelStyle);
        }

        GUILayout.Space(4);
        GUILayout.Label("R = Reset near/far", labelStyle);

        GUILayout.EndArea();
    }

    void InitStyles()
    {
        if (boxStyle != null) return;

        boxStyle = new GUIStyle(GUI.skin.box);
        boxStyle.normal.background = MakeTex(2, 2, new Color(0.04f, 0.06f, 0.1f, 0.82f));

        labelStyle = new GUIStyle(GUI.skin.label);
        labelStyle.fontSize = 13;
        labelStyle.normal.textColor = new Color(0.9f, 0.93f, 0.97f);

        headerStyle = new GUIStyle(GUI.skin.label);
        headerStyle.fontSize = 16;
        headerStyle.fontStyle = FontStyle.Bold;
        headerStyle.normal.textColor = new Color(0.38f, 0.65f, 0.98f);
    }

    Texture2D MakeTex(int width, int height, Color color)
    {
        Color[] pix = new Color[width * height];
        for (int i = 0; i < pix.Length; i++) pix[i] = color;
        Texture2D tex = new Texture2D(width, height);
        tex.SetPixels(pix);
        tex.Apply();
        return tex;
    }
}
