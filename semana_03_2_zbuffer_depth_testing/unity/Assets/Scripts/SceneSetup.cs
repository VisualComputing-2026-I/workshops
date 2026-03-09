using UnityEngine;

/// <summary>
/// SceneSetup.cs
/// Genera programaticamente la escena del taller Z-Buffer:
/// - Multiples objetos superpuestos (cubo, esfera, cono, cilindro)
/// - Suelo de referencia
/// - Planos coplanares para demostrar Z-fighting
/// - Iluminacion basica
///
/// Adjuntar a un GameObject vacio en la escena y ejecutar Play.
/// </summary>
public class SceneSetup : MonoBehaviour
{
    [Header("Materiales")]
    [Tooltip("Material estandar para objetos. Si es null se creara uno por defecto.")]
    public Material defaultMaterial;

    [Tooltip("Material de profundidad (shader DepthVisualization). Asignar manualmente.")]
    public Material depthMaterial;

    // Referencias internas para que otros scripts accedan
    [HideInInspector] public GameObject[] sceneObjects;
    [HideInInspector] public GameObject planeA;
    [HideInInspector] public GameObject planeB;
    [HideInInspector] public GameObject zFightingParent;

    void Awake()
    {
        CreateScene();
    }

    void CreateScene()
    {
        // --- Materiales por defecto ---
        Material matRed    = CreateMat(new Color(0.94f, 0.27f, 0.27f));
        Material matBlue   = CreateMat(new Color(0.23f, 0.51f, 0.96f));
        Material matGreen  = CreateMat(new Color(0.13f, 0.77f, 0.37f));
        Material matPurple = CreateMat(new Color(0.66f, 0.33f, 0.97f));
        Material matFloor  = CreateMat(new Color(0.12f, 0.16f, 0.23f));

        // --- Objetos principales (superpuestos) ---
        GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cube.name = "Cube";
        cube.transform.position = new Vector3(0f, 0.2f, 0f);
        cube.transform.localScale = Vector3.one * 2.4f;
        cube.GetComponent<Renderer>().material = matRed;

        GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        sphere.name = "Sphere";
        sphere.transform.position = new Vector3(1.6f, 0.5f, 0.9f);
        sphere.transform.localScale = Vector3.one * 2.9f;
        sphere.GetComponent<Renderer>().material = matBlue;

        GameObject cylinder = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        cylinder.name = "Cylinder";
        cylinder.transform.position = new Vector3(-1.8f, 0.4f, 1.2f);
        cylinder.transform.localScale = new Vector3(1.2f, 1.4f, 1.2f);
        cylinder.GetComponent<Renderer>().material = matGreen;

        GameObject capsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        capsule.name = "Capsule";
        capsule.transform.position = new Vector3(0.2f, 1.8f, -1.0f);
        capsule.transform.localScale = new Vector3(1.0f, 1.3f, 1.0f);
        capsule.transform.rotation = Quaternion.Euler(60f, 0f, 0f);
        capsule.GetComponent<Renderer>().material = matPurple;

        sceneObjects = new GameObject[] { cube, sphere, cylinder, capsule };

        // --- Suelo ---
        GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
        floor.name = "Floor";
        floor.transform.position = new Vector3(0f, -1f, 0f);
        floor.transform.localScale = new Vector3(2.4f, 1f, 2.4f);
        floor.GetComponent<Renderer>().material = matFloor;

        // --- Planos de Z-fighting ---
        zFightingParent = new GameObject("ZFighting_Planes");
        zFightingParent.transform.position = new Vector3(4.2f, 1f, -2f);

        planeA = GameObject.CreatePrimitive(PrimitiveType.Quad);
        planeA.name = "ZFight_PlaneA";
        planeA.transform.SetParent(zFightingParent.transform);
        planeA.transform.localPosition = Vector3.zero;
        planeA.transform.localScale = Vector3.one * 2.8f;
        planeA.transform.localRotation = Quaternion.Euler(0f, -17f, 0f);
        Material matYellow = CreateMat(new Color(0.98f, 0.75f, 0.14f));
        planeA.GetComponent<Renderer>().material = matYellow;

        planeB = GameObject.CreatePrimitive(PrimitiveType.Quad);
        planeB.name = "ZFight_PlaneB";
        planeB.transform.SetParent(zFightingParent.transform);
        // Separacion minima → Z-fighting
        planeB.transform.localPosition = new Vector3(0f, 0f, 0.001f);
        planeB.transform.localScale = Vector3.one * 2.8f;
        planeB.transform.localRotation = Quaternion.Euler(0f, -17f, 0f);
        Material matWhite = CreateMat(Color.white);
        planeB.GetComponent<Renderer>().material = matWhite;

        // --- Iluminacion ---
        GameObject dirLightGO = new GameObject("DirectionalLight");
        Light dirLight = dirLightGO.AddComponent<Light>();
        dirLight.type = LightType.Directional;
        dirLight.intensity = 1.2f;
        dirLight.color = Color.white;
        dirLightGO.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

        // Posicionar camara si no existe
        Camera cam = Camera.main;
        if (cam != null)
        {
            cam.transform.position = new Vector3(6f, 4.5f, 8f);
            cam.transform.LookAt(new Vector3(0f, 0.6f, 0f));
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 60f;
        }
    }

    Material CreateMat(Color color)
    {
        if (defaultMaterial != null)
        {
            Material mat = new Material(defaultMaterial);
            mat.color = color;
            return mat;
        }

        // Intentar usar URP Lit, fallback a Standard
        Shader shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null)
            shader = Shader.Find("Standard");

        Material m = new Material(shader);
        m.color = color;
        return m;
    }
}
