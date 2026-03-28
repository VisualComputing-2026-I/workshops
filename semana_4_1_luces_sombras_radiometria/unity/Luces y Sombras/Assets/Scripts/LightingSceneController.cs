using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Rendering;

[ExecuteAlways]
public class LightingSceneController : MonoBehaviour
{
    [Header("Ambient Light")]
    [SerializeField] private Color ambientColor = new Color(0.36f, 0.4f, 0.48f, 1f);
    [SerializeField, Range(0f, 2f)] private float ambientIntensity = 0.8f;

    [Header("Directional Light")]
    [SerializeField] private Color directionalColor = new Color(1f, 0.94f, 0.84f, 1f);
    [SerializeField, Range(0f, 4f)] private float directionalIntensity = 1.45f;
    [SerializeField] private Vector3 directionalEuler = new Vector3(48f, -32f, 0f);

    [Header("Point Light")]
    [SerializeField] private Color pointColor = new Color(0.38f, 0.72f, 1f, 1f);
    [SerializeField, Range(0f, 30f)] private float pointIntensity = 16f;
    [SerializeField, Range(2f, 20f)] private float pointRange = 10f;
    [SerializeField] private Vector3 pointPosition = new Vector3(2.5f, 2.8f, -1.4f);

    [Header("Camera Controls")]
    [SerializeField, Range(1f, 12f)] private float cameraMoveSpeed = 4.5f;
    [SerializeField, Range(1f, 4f)] private float cameraSprintMultiplier = 2f;
    [SerializeField, Range(0.02f, 0.3f)] private float cameraLookSensitivity = 0.12f;

    private const string SetupRootName = "Lighting Lab Setup";
    private const string PointLightName = "Point Light";
    private const string GroundName = "Ground";
    private const string MatteSphereName = "Matte Sphere";
    private const string MetallicCubeName = "Metallic Cube";
    private const string GlassCapsuleName = "Glass Capsule";

    private GameObject setupRoot;
    private Light directionalLight;
    private Light pointLight;
    private Camera sceneCamera;
    private float cameraYaw;
    private float cameraPitch;
    private bool cameraRotationInitialized;

    private void OnEnable()
    {
        RebuildScene();
    }

    private void OnValidate()
    {
        RebuildScene();
    }

    private void Update()
    {
        if (Application.isPlaying)
        {
            HandleCameraMovement();
        }
        else
        {
            ApplyLighting();
        }
    }

    private void OnGUI()
    {
        if (!Application.isPlaying)
        {
            return;
        }

        EnsureReferences();

        GUILayout.BeginArea(new Rect(16f, 16f, 330f, 430f), "Lighting Controls", GUI.skin.window);
        GUILayout.Label("Experimenta en tiempo real con las luces y sombras.");

        directionalIntensity = DrawSlider("Intensidad direccional", directionalIntensity, 0f, 4f);

        var newYaw = DrawSlider("Direccion direccional (Y)", directionalEuler.y, -180f, 180f);
        if (!Mathf.Approximately(newYaw, directionalEuler.y))
        {
            directionalEuler.y = newYaw;
        }

        pointIntensity = DrawSlider("Intensidad puntual", pointIntensity, 0f, 30f);
        pointRange = DrawSlider("Rango puntual", pointRange, 2f, 20f);
        ambientIntensity = DrawSlider("Intensidad ambiental", ambientIntensity, 0f, 2f);

        GUILayout.Space(6f);
        GUILayout.Label("Color direccional");
        DrawColorButtons(
            ("Calida", new Color(1f, 0.94f, 0.84f, 1f)),
            ("Atardecer", new Color(1f, 0.67f, 0.46f, 1f)),
            ("Fria", new Color(0.72f, 0.85f, 1f, 1f)),
            color => directionalColor = color);

        GUILayout.Label("Color puntual");
        DrawColorButtons(
            ("Azul", new Color(0.38f, 0.72f, 1f, 1f)),
            ("Magenta", new Color(1f, 0.36f, 0.76f, 1f)),
            ("Verde", new Color(0.47f, 1f, 0.58f, 1f)),
            color => pointColor = color);

        GUILayout.Space(8f);
        GUILayout.Label("Camara");
        GUILayout.Label("Mover: WASD o flechas");
        GUILayout.Label("Subir/Bajar: Q / E");
        GUILayout.Label("Mirar: clic derecho + mouse");
        GUILayout.Label("Acelerar: Shift");

        GUILayout.EndArea();

        ApplyLighting();
    }

    private void RebuildScene()
    {
        if (!isActiveAndEnabled || !gameObject.scene.IsValid())
        {
            return;
        }

        EnsureReferences();
        ConfigureCamera();
        BuildEnvironment();
        ApplyLighting();
    }

    private void EnsureReferences()
    {
        if (setupRoot == null)
        {
            var root = transform.Find(SetupRootName);
            if (root == null)
            {
                root = new GameObject(SetupRootName).transform;
                root.SetParent(transform, false);
            }

            setupRoot = root.gameObject;
        }

        if (directionalLight == null)
        {
            var lightObject = GameObject.Find("Directional Light");
            if (lightObject != null)
            {
                directionalLight = lightObject.GetComponent<Light>();
            }
        }

        if (directionalLight == null)
        {
            var lightObject = new GameObject("Directional Light");
            directionalLight = lightObject.AddComponent<Light>();
            lightObject.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
        }

        if (pointLight == null)
        {
            var pointLightTransform = setupRoot.transform.Find(PointLightName);
            if (pointLightTransform == null)
            {
                pointLightTransform = new GameObject(PointLightName).transform;
                pointLightTransform.SetParent(setupRoot.transform, false);
            }

            pointLight = EnsureComponent<Light>(pointLightTransform.gameObject);
        }

        if (sceneCamera == null)
        {
            sceneCamera = Camera.main;
            if (sceneCamera == null)
            {
                sceneCamera = FindFirstObjectByType<Camera>();
            }
        }
    }

    private void ConfigureCamera()
    {
        if (sceneCamera == null)
        {
            return;
        }

        sceneCamera.transform.SetPositionAndRotation(
            new Vector3(0f, 2.35f, -8.5f),
            Quaternion.Euler(11f, 0f, 0f));
        var currentEuler = sceneCamera.transform.rotation.eulerAngles;
        cameraPitch = NormalizeAngle(currentEuler.x);
        cameraYaw = NormalizeAngle(currentEuler.y);
        cameraRotationInitialized = true;
        sceneCamera.fieldOfView = 54f;
        sceneCamera.nearClipPlane = 0.1f;
        sceneCamera.farClipPlane = 60f;
        sceneCamera.clearFlags = CameraClearFlags.SolidColor;
        sceneCamera.backgroundColor = new Color(0.08f, 0.1f, 0.13f, 1f);
    }

    private void BuildEnvironment()
    {
        var ground = GetOrCreatePrimitive(GroundName, PrimitiveType.Cube);
        ConfigureObject(ground, new Vector3(0f, -0.05f, 0f), Vector3.zero, new Vector3(10f, 0.1f, 10f));
        ApplyMaterial(ground, "Ground_Mat", new Color(0.17f, 0.19f, 0.24f, 1f), 0.05f, 0.28f, false);

        var matteSphere = GetOrCreatePrimitive(MatteSphereName, PrimitiveType.Sphere);
        ConfigureObject(matteSphere, new Vector3(-2.4f, 0.9f, 0.55f), Vector3.zero, Vector3.one * 1.8f);
        ApplyMaterial(matteSphere, "MatteSphere_Mat", new Color(0.87f, 0.33f, 0.25f, 1f), 0f, 0.08f, false);

        var metallicCube = GetOrCreatePrimitive(MetallicCubeName, PrimitiveType.Cube);
        ConfigureObject(metallicCube, new Vector3(0f, 0.95f, 0f), new Vector3(10f, 36f, -6f), new Vector3(1.7f, 1.7f, 1.7f));
        ApplyMaterial(metallicCube, "MetallicCube_Mat", new Color(0.72f, 0.78f, 0.84f, 1f), 1f, 0.92f, false);

        var glassCapsule = GetOrCreatePrimitive(GlassCapsuleName, PrimitiveType.Capsule);
        ConfigureObject(glassCapsule, new Vector3(2.4f, 1.2f, -0.4f), new Vector3(0f, -18f, 0f), new Vector3(1.15f, 2.2f, 1.15f));
        ApplyMaterial(glassCapsule, "GlassCapsule_Mat", new Color(0.38f, 0.9f, 1f, 0.46f), 0.12f, 0.95f, true);
    }

    private void ApplyLighting()
    {
        EnsureReferences();

        RenderSettings.ambientMode = AmbientMode.Flat;
        RenderSettings.ambientIntensity = ambientIntensity;
        RenderSettings.ambientLight = ambientColor * ambientIntensity;

        directionalLight.type = LightType.Directional;
        directionalLight.color = directionalColor;
        directionalLight.intensity = directionalIntensity;
        directionalLight.shadows = LightShadows.Soft;
        directionalLight.shadowStrength = 1f;
        directionalLight.shadowBias = 0.04f;
        directionalLight.shadowNormalBias = 0.3f;
        directionalLight.transform.SetPositionAndRotation(
            new Vector3(0f, 3f, 0f),
            Quaternion.Euler(directionalEuler));
        RenderSettings.sun = directionalLight;

        pointLight.type = LightType.Point;
        pointLight.color = pointColor;
        pointLight.intensity = pointIntensity;
        pointLight.range = pointRange;
        pointLight.shadows = LightShadows.Soft;
        pointLight.shadowStrength = 0.85f;
        pointLight.shadowBias = 0.03f;
        pointLight.shadowNormalBias = 0.2f;
        pointLight.transform.localPosition = pointPosition;
        pointLight.transform.localRotation = Quaternion.identity;
    }

    private void HandleCameraMovement()
    {
        EnsureReferences();
        if (sceneCamera == null || Keyboard.current == null)
        {
            return;
        }

        if (!cameraRotationInitialized)
        {
            var currentEuler = sceneCamera.transform.rotation.eulerAngles;
            cameraPitch = NormalizeAngle(currentEuler.x);
            cameraYaw = NormalizeAngle(currentEuler.y);
            cameraRotationInitialized = true;
        }

        var keyboard = Keyboard.current;
        var mouse = Mouse.current;

        var moveInput = Vector3.zero;
        if (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed)
        {
            moveInput.z += 1f;
        }
        if (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed)
        {
            moveInput.z -= 1f;
        }
        if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed)
        {
            moveInput.x += 1f;
        }
        if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed)
        {
            moveInput.x -= 1f;
        }
        if (keyboard.eKey.isPressed)
        {
            moveInput.y += 1f;
        }
        if (keyboard.qKey.isPressed)
        {
            moveInput.y -= 1f;
        }

        if (moveInput.sqrMagnitude > 1f)
        {
            moveInput.Normalize();
        }

        var speed = cameraMoveSpeed;
        if (keyboard.leftShiftKey.isPressed || keyboard.rightShiftKey.isPressed)
        {
            speed *= cameraSprintMultiplier;
        }

        var cameraTransform = sceneCamera.transform;
        var planarForward = Vector3.ProjectOnPlane(cameraTransform.forward, Vector3.up).normalized;
        if (planarForward.sqrMagnitude < 0.0001f)
        {
            planarForward = Vector3.forward;
        }

        var planarRight = Vector3.ProjectOnPlane(cameraTransform.right, Vector3.up).normalized;
        if (planarRight.sqrMagnitude < 0.0001f)
        {
            planarRight = Vector3.right;
        }

        var worldMove = planarRight * moveInput.x + Vector3.up * moveInput.y + planarForward * moveInput.z;
        cameraTransform.position += worldMove * speed * Time.deltaTime;

        if (mouse != null && mouse.rightButton.isPressed)
        {
            var mouseDelta = mouse.delta.ReadValue();
            cameraYaw += mouseDelta.x * cameraLookSensitivity;
            cameraPitch -= mouseDelta.y * cameraLookSensitivity;
            cameraPitch = Mathf.Clamp(cameraPitch, -80f, 80f);
            cameraTransform.rotation = Quaternion.Euler(cameraPitch, cameraYaw, 0f);
        }
    }

    private GameObject GetOrCreatePrimitive(string objectName, PrimitiveType primitiveType)
    {
        var child = setupRoot.transform.Find(objectName);
        GameObject target;

        if (child == null)
        {
            target = GameObject.CreatePrimitive(primitiveType);
            target.name = objectName;
            target.transform.SetParent(setupRoot.transform, false);
        }
        else
        {
            target = child.gameObject;
        }

        var renderer = target.GetComponent<MeshRenderer>();
        if (renderer != null)
        {
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;
        }

        return target;
    }

    private static void ConfigureObject(GameObject target, Vector3 position, Vector3 euler, Vector3 scale)
    {
        target.transform.localPosition = position;
        target.transform.localRotation = Quaternion.Euler(euler);
        target.transform.localScale = scale;
    }

    private static T EnsureComponent<T>(GameObject target) where T : Component
    {
        var component = target.GetComponent<T>();
        if (component == null)
        {
            component = target.AddComponent<T>();
        }

        return component;
    }

    private static float DrawSlider(string label, float value, float min, float max)
    {
        GUILayout.Label($"{label}: {value:0.00}");
        return GUILayout.HorizontalSlider(value, min, max);
    }

    private static float NormalizeAngle(float angle)
    {
        if (angle > 180f)
        {
            angle -= 360f;
        }

        return angle;
    }

    private static void DrawColorButtons(
        (string label, Color color) left,
        (string label, Color color) center,
        (string label, Color color) right,
        System.Action<Color> setter)
    {
        GUILayout.BeginHorizontal();

        DrawColorButton(left.label, left.color, setter);
        DrawColorButton(center.label, center.color, setter);
        DrawColorButton(right.label, right.color, setter);

        GUILayout.EndHorizontal();
    }

    private static void DrawColorButton(string label, Color color, System.Action<Color> setter)
    {
        var previous = GUI.backgroundColor;
        GUI.backgroundColor = color;

        if (GUILayout.Button(label, GUILayout.Height(24f)))
        {
            setter(color);
        }

        GUI.backgroundColor = previous;
    }

    private static Material CreateLitMaterial(Color color, float metallic, float smoothness)
    {
        var shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null)
        {
            return null;
        }

        var material = new Material(shader);
        material.color = color;
        material.SetColor("_BaseColor", color);
        material.SetFloat("_Metallic", metallic);
        material.SetFloat("_Smoothness", smoothness);
        return material;
    }

    private static Material CreateTransparentMaterial(Color color, float metallic, float smoothness)
    {
        var material = CreateLitMaterial(color, metallic, smoothness);
        material.SetFloat("_Surface", 1f);
        material.SetFloat("_Blend", 0f);
        material.SetInt("_SrcBlend", (int)BlendMode.SrcAlpha);
        material.SetInt("_DstBlend", (int)BlendMode.OneMinusSrcAlpha);
        material.SetInt("_ZWrite", 0);
        material.DisableKeyword("_ALPHATEST_ON");
        material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
        material.renderQueue = (int)RenderQueue.Transparent;
        return material;
    }

    private static void ApplyMaterial(
        GameObject target,
        string materialName,
        Color color,
        float metallic,
        float smoothness,
        bool transparent)
    {
        var renderer = target.GetComponent<MeshRenderer>();
        if (renderer == null)
        {
            return;
        }

        var material = renderer.sharedMaterial;
        if (material == null || material.name != materialName)
        {
            material = transparent
                ? CreateTransparentMaterial(color, metallic, smoothness)
                : CreateLitMaterial(color, metallic, smoothness);

            if (material == null)
            {
                return;
            }

            material.name = materialName;
            renderer.sharedMaterial = material;
        }
        else
        {
            material.color = color;
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
        }

        if (transparent)
        {
            material.color = color;
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_Surface", 1f);
            material.SetFloat("_Blend", 0f);
            material.SetInt("_SrcBlend", (int)BlendMode.SrcAlpha);
            material.SetInt("_DstBlend", (int)BlendMode.OneMinusSrcAlpha);
            material.SetInt("_ZWrite", 0);
            material.DisableKeyword("_ALPHATEST_ON");
            material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            material.renderQueue = (int)RenderQueue.Transparent;
        }
        else
        {
            material.color = color;
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_Surface", 0f);
            material.SetInt("_ZWrite", 1);
            material.renderQueue = -1;
        }
    }
}
