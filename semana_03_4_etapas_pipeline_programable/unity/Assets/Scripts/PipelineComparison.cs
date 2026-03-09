using UnityEngine;

public class PipelineComparison : MonoBehaviour
{
    [Header("Materiales — arrastra aquí")]
    public Material matFijo;    // URP/Lit  (pipeline fijo)
    public Material matCustom;  // S2_FragmentColor (pipeline programable)

    private GameObject   _esferaFija;
    private GameObject   _esferaCustom;
    private MeshRenderer _rendererCustom;
    private bool         _mostandoCustom = true;

    void Start()
    {
        CrearEsferas();
    }

    void Update()
    {
        float rot = 20f * Time.deltaTime;
        if (_esferaFija   != null) _esferaFija  .transform.Rotate(Vector3.up, rot);
        if (_esferaCustom != null) _esferaCustom.transform.Rotate(Vector3.up, rot);
    }

    void OnGUI()
    {
        if (matFijo == null || matCustom == null)
        {
            GUI.color = Color.red;
            GUI.Label(new Rect(10, 10, 500, 30),
                      "⚠ Asigna 'matFijo' y 'matCustom' en el Inspector del script.");
            return;
        }

        GUIStyle estiloBoton = new GUIStyle(GUI.skin.button);
        estiloBoton.fontSize  = 15;
        estiloBoton.fontStyle = FontStyle.Bold;

        GUIStyle estiloLabel = new GUIStyle(GUI.skin.label);
        estiloLabel.fontSize  = 13;
        estiloLabel.fontStyle = FontStyle.Bold;
        estiloLabel.normal.textColor = Color.white;
        estiloLabel.alignment = TextAnchor.MiddleCenter;

        GUI.Label(new Rect(0, 30, Screen.width / 2f, 25),
                  "PIPELINE FIJO  (URP/Lit)", estiloLabel);
        GUI.Label(new Rect(Screen.width / 2f, 30, Screen.width / 2f, 25),
                  _mostandoCustom ? "PIPELINE PROGRAMABLE  (HLSL Manual)"
                                  : "PIPELINE FIJO  (mismo shader — para comparar)",
                  estiloLabel);

        float bw = 380f, bh = 45f;
        float bx = (Screen.width  - bw) / 2f;
        float by =  Screen.height - bh - 15f;

        string textoBoton = _mostandoCustom
            ? "▶  Cambiar esfera derecha → Pipeline FIJO"
            : "▶  Cambiar esfera derecha → Pipeline PROGRAMABLE";

        if (GUI.Button(new Rect(bx, by, bw, bh), textoBoton, estiloBoton))
        {
            _mostandoCustom    = !_mostandoCustom;
            _rendererCustom.sharedMaterial = _mostandoCustom ? matCustom : matFijo;
        }

        GUIStyle estiloInfo = new GUIStyle(GUI.skin.box);
        estiloInfo.fontSize  = 11;
        estiloInfo.alignment = TextAnchor.UpperLeft;
        estiloInfo.normal.textColor = Color.white;

        string info =
            "Pipeline FIJO (URP/Lit):\n" +
            " + Iluminación PBR automática\n" +
            " + Sombras, GI, reflecciones gratis\n" +
            " - Sin control sobre vértices\n" +
            " - No se puede animar la geometría\n\n" +
            "Pipeline PROGRAMABLE (HLSL):\n" +
            " + Control total sobre cada vértice\n" +
            " + Efectos procedurales custom\n" +
            " + Deformaciones en tiempo real\n" +
            " - Hay que implementar iluminación";

        GUI.Box(new Rect(10, Screen.height - 220, 280, 210), info, estiloInfo);
    }

    void CrearEsferas()
    {
        if (_esferaFija   != null) Destroy(_esferaFija);
        if (_esferaCustom != null) Destroy(_esferaCustom);

        _esferaFija = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        _esferaFija.name = "Esfera_PipelineFijo";
        _esferaFija.transform.SetParent(transform);
        _esferaFija.transform.localPosition = new Vector3(-1.5f, 0f, 0f);
        if (matFijo != null)
            _esferaFija.GetComponent<MeshRenderer>().sharedMaterial = matFijo;

        _esferaCustom = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        _esferaCustom.name = "Esfera_PipelineProgramable";
        _esferaCustom.transform.SetParent(transform);
        _esferaCustom.transform.localPosition = new Vector3(1.5f, 0f, 0f);
        _rendererCustom = _esferaCustom.GetComponent<MeshRenderer>();
        if (matCustom != null)
            _rendererCustom.sharedMaterial = matCustom;

        if (FindFirstObjectByType<Light>() == null)
        {
            var go       = new GameObject("Luz_Direccional");
            var luz      = go.AddComponent<Light>();
            luz.type      = LightType.Directional;
            luz.intensity = 1.2f;
            go.transform.rotation = Quaternion.Euler(45f, -45f, 0f);
        }
    }

    void OnDestroy()
    {
        if (_esferaFija   != null) Destroy(_esferaFija);
        if (_esferaCustom != null) Destroy(_esferaCustom);
    }
}
