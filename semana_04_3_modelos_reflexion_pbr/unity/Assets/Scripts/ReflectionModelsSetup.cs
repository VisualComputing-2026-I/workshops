using UnityEngine;

/// <summary>
/// Configura la escena con esferas que usan diferentes modelos de iluminacion.
/// Crea 4 esferas principales: Lambert, Phong, Blinn-Phong, y PBR (Standard).
/// Tambien crea una grilla de esferas PBR con variaciones de metalness/roughness.
/// </summary>
public class ReflectionModelsSetup : MonoBehaviour
{
    [Header("Shaders")]
    public Shader lambertShader;
    public Shader phongShader;
    public Shader blinnPhongShader;

    [Header("Sphere Settings")]
    public float sphereRadius = 1.0f;
    public int sphereSegments = 64;
    public float sphereSpacing = 3.5f;

    [Header("PBR Grid Settings")]
    public bool createPBRGrid = true;
    public int gridColumns = 5;
    public float gridSphereRadius = 0.6f;
    public float gridSpacing = 1.8f;

    [Header("Material Colors")]
    public Color diffuseColor = new Color(0.8f, 0.2f, 0.2f, 1f);
    public Color specularColor = Color.white;
    public Color ambientColor = new Color(0.1f, 0.1f, 0.15f, 1f);

    [Header("Scene References")]
    public Light mainLight;
    public Transform sphereParent;
    public Transform pbrGridParent;

    // Referencias a las esferas principales
    private GameObject lambertSphere;
    private GameObject phongSphere;
    private GameObject blinnSphere;
    private GameObject pbrSphere;

    // Materiales
    private Material lambertMaterial;
    private Material phongMaterial;
    private Material blinnMaterial;
    private Material pbrMaterial;

    void Start()
    {
        SetupScene();
    }

    void SetupScene()
    {
        // Crear contenedor si no existe
        if (sphereParent == null)
        {
            sphereParent = new GameObject("ModelSpheres").transform;
        }

        // Cargar shaders si no estan asignados
        if (lambertShader == null) lambertShader = Shader.Find("Custom/LambertDiffuse");
        if (phongShader == null) phongShader = Shader.Find("Custom/PhongSpecular");
        if (blinnPhongShader == null) blinnPhongShader = Shader.Find("Custom/BlinnPhongSpecular");

        // Crear esferas principales
        CreateMainSpheres();

        // Crear grilla PBR
        if (createPBRGrid)
        {
            CreatePBRGrid();
        }

        // Crear luz si no existe
        if (mainLight == null)
        {
            CreateMainLight();
        }

        // Crear suelo
        CreateFloor();
    }

    void CreateMainSpheres()
    {
        float startX = -sphereSpacing * 1.5f;

        // Lambert
        lambertSphere = CreateSphere("Lambert", new Vector3(startX, 0, 0));
        lambertMaterial = new Material(lambertShader);
        lambertMaterial.SetColor("_DiffuseColor", diffuseColor);
        lambertMaterial.SetColor("_AmbientColor", ambientColor);
        lambertSphere.GetComponent<Renderer>().material = lambertMaterial;
        CreateLabel(lambertSphere.transform, "Lambert (Diffuse)");

        // Phong
        phongSphere = CreateSphere("Phong", new Vector3(startX + sphereSpacing, 0, 0));
        phongMaterial = new Material(phongShader);
        phongMaterial.SetColor("_DiffuseColor", diffuseColor);
        phongMaterial.SetColor("_SpecularColor", specularColor);
        phongMaterial.SetColor("_AmbientColor", ambientColor);
        phongMaterial.SetFloat("_Shininess", 32f);
        phongSphere.GetComponent<Renderer>().material = phongMaterial;
        CreateLabel(phongSphere.transform, "Phong");

        // Blinn-Phong
        blinnSphere = CreateSphere("BlinnPhong", new Vector3(startX + sphereSpacing * 2, 0, 0));
        blinnMaterial = new Material(blinnPhongShader);
        blinnMaterial.SetColor("_DiffuseColor", diffuseColor);
        blinnMaterial.SetColor("_SpecularColor", specularColor);
        blinnMaterial.SetColor("_AmbientColor", ambientColor);
        blinnMaterial.SetFloat("_Shininess", 32f);
        blinnSphere.GetComponent<Renderer>().material = blinnMaterial;
        CreateLabel(blinnSphere.transform, "Blinn-Phong");

        // PBR (Standard)
        pbrSphere = CreateSphere("PBR", new Vector3(startX + sphereSpacing * 3, 0, 0));
        pbrMaterial = new Material(Shader.Find("Standard"));
        pbrMaterial.SetColor("_Color", diffuseColor);
        pbrMaterial.SetFloat("_Metallic", 0f);
        pbrMaterial.SetFloat("_Glossiness", 0.6f);
        pbrSphere.GetComponent<Renderer>().material = pbrMaterial;
        CreateLabel(pbrSphere.transform, "PBR (Standard)");
    }

    void CreatePBRGrid()
    {
        if (pbrGridParent == null)
        {
            pbrGridParent = new GameObject("PBRGrid").transform;
            pbrGridParent.position = new Vector3(0, -3f, 0);
        }

        // Fila superior: variaciones de roughness (dielectrico)
        for (int i = 0; i < gridColumns; i++)
        {
            float roughness = (float)i / (gridColumns - 1);
            float x = (i - (gridColumns - 1) * 0.5f) * gridSpacing;

            GameObject sphere = CreateSphere($"PBR_Dielectric_R{roughness:F2}",
                new Vector3(x, gridSpacing * 0.5f, 0), gridSphereRadius);
            sphere.transform.SetParent(pbrGridParent);

            Material mat = new Material(Shader.Find("Standard"));
            mat.SetColor("_Color", new Color(0.23f, 0.51f, 0.96f)); // Azul
            mat.SetFloat("_Metallic", 0f);
            mat.SetFloat("_Glossiness", 1f - roughness);
            sphere.GetComponent<Renderer>().material = mat;
        }

        // Fila inferior: variaciones de roughness (metal)
        for (int i = 0; i < gridColumns; i++)
        {
            float roughness = (float)i / (gridColumns - 1);
            float x = (i - (gridColumns - 1) * 0.5f) * gridSpacing;

            GameObject sphere = CreateSphere($"PBR_Metal_R{roughness:F2}",
                new Vector3(x, -gridSpacing * 0.5f, 0), gridSphereRadius);
            sphere.transform.SetParent(pbrGridParent);

            Material mat = new Material(Shader.Find("Standard"));
            mat.SetColor("_Color", new Color(0.98f, 0.75f, 0.15f)); // Dorado
            mat.SetFloat("_Metallic", 1f);
            mat.SetFloat("_Glossiness", 1f - roughness);
            sphere.GetComponent<Renderer>().material = mat;
        }

        // Etiquetas
        CreateWorldLabel(pbrGridParent, "Dielectrico (Metalness = 0)",
            new Vector3(-gridSpacing * 2.5f, gridSpacing * 0.5f, 0));
        CreateWorldLabel(pbrGridParent, "Metal (Metalness = 1)",
            new Vector3(-gridSpacing * 2.5f, -gridSpacing * 0.5f, 0));
    }

    GameObject CreateSphere(string name, Vector3 position, float radius = -1)
    {
        if (radius < 0) radius = sphereRadius;

        GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        sphere.name = name;
        sphere.transform.position = position;
        sphere.transform.localScale = Vector3.one * radius * 2;
        sphere.transform.SetParent(sphereParent);

        return sphere;
    }

    void CreateMainLight()
    {
        GameObject lightObj = new GameObject("Main Light");
        mainLight = lightObj.AddComponent<Light>();
        mainLight.type = LightType.Directional;
        mainLight.transform.rotation = Quaternion.Euler(50, -30, 0);
        mainLight.intensity = 1.2f;
        mainLight.color = Color.white;
    }

    void CreateFloor()
    {
        GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
        floor.name = "Floor";
        floor.transform.position = new Vector3(0, -sphereRadius - 0.5f, 0);
        floor.transform.localScale = new Vector3(3, 1, 3);

        Material floorMat = new Material(Shader.Find("Standard"));
        floorMat.SetColor("_Color", new Color(0.12f, 0.14f, 0.23f));
        floorMat.SetFloat("_Metallic", 0.05f);
        floorMat.SetFloat("_Glossiness", 0.15f);
        floor.GetComponent<Renderer>().material = floorMat;
    }

    void CreateLabel(Transform parent, string text)
    {
        // En un proyecto real usarias TextMeshPro o UI World Space
        // Por simplicidad, creamos un GameObject vacio con el nombre
        GameObject label = new GameObject($"Label_{text}");
        label.transform.SetParent(parent);
        label.transform.localPosition = Vector3.up * (sphereRadius + 0.5f);
    }

    void CreateWorldLabel(Transform parent, string text, Vector3 localPos)
    {
        GameObject label = new GameObject($"Label_{text}");
        label.transform.SetParent(parent);
        label.transform.localPosition = localPos;
    }

    // API publica para controlar desde UI
    public void SetShininess(float value)
    {
        if (phongMaterial != null) phongMaterial.SetFloat("_Shininess", value);
        if (blinnMaterial != null) blinnMaterial.SetFloat("_Shininess", value);
    }

    public void SetDiffuseColor(Color color)
    {
        diffuseColor = color;
        if (lambertMaterial != null) lambertMaterial.SetColor("_DiffuseColor", color);
        if (phongMaterial != null) phongMaterial.SetColor("_DiffuseColor", color);
        if (blinnMaterial != null) blinnMaterial.SetColor("_DiffuseColor", color);
        if (pbrMaterial != null) pbrMaterial.SetColor("_Color", color);
    }

    public void SetSpecularColor(Color color)
    {
        specularColor = color;
        if (phongMaterial != null) phongMaterial.SetColor("_SpecularColor", color);
        if (blinnMaterial != null) blinnMaterial.SetColor("_SpecularColor", color);
    }

    public void SetPBRMetalness(float value)
    {
        if (pbrMaterial != null) pbrMaterial.SetFloat("_Metallic", value);
    }

    public void SetPBRRoughness(float value)
    {
        if (pbrMaterial != null) pbrMaterial.SetFloat("_Glossiness", 1f - value);
    }
}
