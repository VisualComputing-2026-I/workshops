using UnityEngine;
using UnityEngine.UI;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

[ExecuteAlways]
public class InterpolationDemoController : MonoBehaviour
{
    private enum PathMode
    {
        LinearLerp,
        Bezier
    }

    private enum EasingMode
    {
        Linear,
        SmoothStep,
        AnimationCurve
    }

    [Header("Playback")]
    [SerializeField] private PathMode pathMode = PathMode.LinearLerp;
    [SerializeField] private EasingMode easingMode = EasingMode.AnimationCurve;
    [SerializeField] private float duration = 4f;
    [SerializeField] private bool pingPong = true;
    [SerializeField] private bool autoConfigureCamera = true;
    [SerializeField] private bool enableShortcuts = true;
    [SerializeField, Range(0f, 1f)] private float previewT;

    [Header("Interpolation")]
    [SerializeField] private AnimationCurve customCurve = AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);
    [SerializeField] private Vector3 startRotationEuler = new Vector3(0f, 0f, 0f);
    [SerializeField] private Vector3 endRotationEuler = new Vector3(0f, 180f, 25f);

    [Header("Generated References")]
    [SerializeField] private Transform generatedRoot;
    [SerializeField] private Transform movingSphere;
    [SerializeField] private Transform pointA;
    [SerializeField] private Transform pointB;
    [SerializeField] private Transform controlPointA;
    [SerializeField] private Transform controlPointB;
    [SerializeField] private LineRenderer pathRenderer;
    [SerializeField] private LineRenderer helperRenderer;
    [SerializeField] private RectTransform progressFill;
    [SerializeField] private Text titleLabel;
    [SerializeField] private Text statusLabel;
    [SerializeField] private Text shortcutLabel;

    private float elapsed;
    private bool isSettingUp;
    private Material runtimeLineMaterial;

    private void Reset()
    {
        EnsureDefaults();
        EnsureSceneSetup();
        ApplyMotion(previewT);
    }

    private void OnEnable()
    {
        EnsureDefaults();
        EnsureSceneSetup();
        ApplyMotion(previewT);
    }

    private void OnValidate()
    {
        EnsureDefaults();
        EnsureSceneSetup();
        ApplyMotion(Application.isPlaying ? GetPingPongTime() : previewT);
    }

    private void Update()
    {
        if (isSettingUp)
        {
            return;
        }

        EnsureSceneSetup();

        if (Application.isPlaying)
        {
            elapsed += Time.deltaTime;
            HandleShortcuts();
            ApplyMotion(GetPingPongTime());
            return;
        }

        ApplyMotion(previewT);
    }

    private void OnDrawGizmos()
    {
        if (!ArePointsReady())
        {
            return;
        }

        Gizmos.color = new Color(0.15f, 0.75f, 1f, 1f);
        Gizmos.DrawSphere(pointA.position, 0.18f);

        Gizmos.color = new Color(1f, 0.55f, 0.15f, 1f);
        Gizmos.DrawSphere(pointB.position, 0.18f);

        Gizmos.color = new Color(0.2f, 1f, 0.65f, 1f);
        Gizmos.DrawSphere(controlPointA.position, 0.12f);
        Gizmos.DrawSphere(controlPointB.position, 0.12f);

        Gizmos.color = new Color(1f, 1f, 1f, 0.5f);
        Gizmos.DrawLine(pointA.position, pointB.position);

        Gizmos.color = new Color(0.2f, 1f, 0.65f, 0.8f);
        Gizmos.DrawLine(pointA.position, controlPointA.position);
        Gizmos.DrawLine(controlPointA.position, controlPointB.position);
        Gizmos.DrawLine(controlPointB.position, pointB.position);

        Vector3 previous = pointA.position;
        for (int i = 1; i <= 24; i++)
        {
            float t = i / 24f;
            Vector3 current = EvaluateBezier(t);
            Gizmos.DrawLine(previous, current);
            previous = current;
        }
    }

    private void OnDestroy()
    {
        if (runtimeLineMaterial == null)
        {
            return;
        }

        if (Application.isPlaying)
        {
            Destroy(runtimeLineMaterial);
        }
        else
        {
            DestroyImmediate(runtimeLineMaterial);
        }
    }

    private void EnsureDefaults()
    {
        duration = Mathf.Max(0.5f, duration);

        if (customCurve == null || customCurve.length == 0)
        {
            customCurve = AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);
        }
    }

    private void EnsureSceneSetup()
    {
        if (isSettingUp)
        {
            return;
        }

        isSettingUp = true;

        try
        {
            generatedRoot = EnsureChildTransform(ref generatedRoot, transform, "Generated Demo", Vector3.zero, Vector3.zero, Vector3.one);

            EnsureEnvironment();
            EnsureMotionAnchors();
            EnsureMovingObject();
            EnsurePathRenderers();
            EnsureOverlay();

            if (autoConfigureCamera)
            {
                ConfigureCamera();
            }

            RefreshPathLines();
            UpdateOverlay(previewT, EvaluateEasing(previewT));
        }
        finally
        {
            isSettingUp = false;
        }
    }

    private void EnsureEnvironment()
    {
        EnsurePrimitiveChild(
            generatedRoot,
            "Floor",
            PrimitiveType.Plane,
            new Vector3(0f, 0f, 0f),
            Vector3.zero,
            new Vector3(1.4f, 1f, 1.1f));
    }

    private void EnsureMotionAnchors()
    {
        pointA = EnsurePrimitiveChild(
            generatedRoot,
            "Point A",
            PrimitiveType.Cube,
            new Vector3(-4f, 0.6f, -1.5f),
            Vector3.zero,
            Vector3.one * 0.35f).transform;

        pointB = EnsurePrimitiveChild(
            generatedRoot,
            "Point B",
            PrimitiveType.Cube,
            new Vector3(4f, 0.6f, 1.5f),
            Vector3.zero,
            Vector3.one * 0.35f).transform;

        controlPointA = EnsurePrimitiveChild(
            generatedRoot,
            "Bezier Control A",
            PrimitiveType.Sphere,
            new Vector3(-1.5f, 2.8f, -3f),
            Vector3.zero,
            Vector3.one * 0.22f).transform;

        controlPointB = EnsurePrimitiveChild(
            generatedRoot,
            "Bezier Control B",
            PrimitiveType.Sphere,
            new Vector3(1.5f, 2f, 3f),
            Vector3.zero,
            Vector3.one * 0.22f).transform;
    }

    private void EnsureMovingObject()
    {
        movingSphere = EnsurePrimitiveChild(
            generatedRoot,
            "Moving Sphere",
            PrimitiveType.Sphere,
            pointA != null ? pointA.position + Vector3.up * 0.6f : new Vector3(-4f, 1.2f, -1.5f),
            Vector3.zero,
            Vector3.one * 0.9f).transform;

        Transform marker = movingSphere.Find("Orientation Marker");
        if (marker == null)
        {
            GameObject markerObject = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            marker = markerObject.transform;
            marker.SetParent(movingSphere, false);
            marker.name = "Orientation Marker";
        }

        marker.localPosition = new Vector3(0.45f, 0f, 0f);
        marker.localRotation = Quaternion.Euler(0f, 0f, 90f);
        marker.localScale = new Vector3(0.12f, 0.3f, 0.12f);
    }

    private void EnsurePathRenderers()
    {
        pathRenderer = EnsureLineRenderer(
            ref pathRenderer,
            "Path Renderer",
            new Color(0.1f, 0.85f, 1f, 1f),
            0.12f,
            32);

        helperRenderer = EnsureLineRenderer(
            ref helperRenderer,
            "Bezier Helper Renderer",
            new Color(0.9f, 0.95f, 1f, 0.4f),
            0.05f,
            4);
    }

    private void EnsureOverlay()
    {
        Transform overlayRoot = generatedRoot.Find("Overlay Canvas");
        Canvas canvas;

        if (overlayRoot == null)
        {
            GameObject canvasObject = new GameObject("Overlay Canvas", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            overlayRoot = canvasObject.transform;
            overlayRoot.SetParent(generatedRoot, false);
            canvas = canvasObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;

            CanvasScaler scaler = canvasObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920f, 1080f);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = 0.5f;
        }
        else
        {
            canvas = overlayRoot.GetComponent<Canvas>();
        }

        RectTransform panel = EnsureUiObject<Image>(overlayRoot, "Info Panel").rectTransform;
        panel.anchorMin = new Vector2(0f, 1f);
        panel.anchorMax = new Vector2(0f, 1f);
        panel.pivot = new Vector2(0f, 1f);
        panel.anchoredPosition = new Vector2(30f, -30f);
        panel.sizeDelta = new Vector2(520f, 190f);

        Image panelImage = panel.GetComponent<Image>();
        panelImage.color = new Color(0.06f, 0.1f, 0.16f, 0.82f);

        titleLabel = EnsureText(
            panel,
            ref titleLabel,
            "Title",
            "Interpolacion de movimiento",
            26,
            FontStyle.Bold,
            new Vector2(18f, -18f),
            new Vector2(484f, 32f));

        statusLabel = EnsureText(
            panel,
            ref statusLabel,
            "Status",
            string.Empty,
            18,
            FontStyle.Normal,
            new Vector2(18f, -58f),
            new Vector2(484f, 72f));

        shortcutLabel = EnsureText(
            panel,
            ref shortcutLabel,
            "Shortcuts",
            "Espacio: cambiar trayecto | Tab: cambiar easing",
            16,
            FontStyle.Italic,
            new Vector2(18f, -150f),
            new Vector2(484f, 22f));

        RectTransform barBackground = EnsureUiObject<Image>(panel, "Progress Background").rectTransform;
        barBackground.anchorMin = new Vector2(0f, 1f);
        barBackground.anchorMax = new Vector2(0f, 1f);
        barBackground.pivot = new Vector2(0f, 1f);
        barBackground.anchoredPosition = new Vector2(18f, -122f);
        barBackground.sizeDelta = new Vector2(484f, 14f);
        barBackground.GetComponent<Image>().color = new Color(1f, 1f, 1f, 0.16f);

        Image fillImage = EnsureUiObject<Image>(barBackground, "Progress Fill");
        progressFill = fillImage.rectTransform;
        progressFill.anchorMin = new Vector2(0f, 0f);
        progressFill.anchorMax = new Vector2(0f, 1f);
        progressFill.pivot = new Vector2(0f, 0.5f);
        progressFill.anchoredPosition = Vector2.zero;
        progressFill.sizeDelta = new Vector2(0f, 0f);
        fillImage.color = new Color(0.15f, 0.85f, 1f, 0.95f);
    }

    private void ConfigureCamera()
    {
        Camera activeCamera = Camera.main;
        if (activeCamera == null)
        {
            activeCamera = FindFirstObjectByType<Camera>();
        }

        if (activeCamera == null)
        {
            return;
        }

        Transform cameraTransform = activeCamera.transform;
        cameraTransform.position = new Vector3(0f, 4.8f, -12f);
        cameraTransform.rotation = Quaternion.Euler(17f, 0f, 0f);
    }

    private void ApplyMotion(float normalizedTime)
    {
        if (!ArePointsReady() || movingSphere == null)
        {
            return;
        }

        float easedT = EvaluateEasing(normalizedTime);
        Vector3 position = pathMode == PathMode.Bezier
            ? EvaluateBezier(easedT)
            : Vector3.Lerp(pointA.position, pointB.position, easedT);

        movingSphere.position = position + Vector3.up * 0.6f;
        movingSphere.rotation = Quaternion.Slerp(
            Quaternion.Euler(startRotationEuler),
            Quaternion.Euler(endRotationEuler),
            easedT);

        RefreshPathLines();
        UpdateOverlay(normalizedTime, easedT);
    }

    private float EvaluateEasing(float t)
    {
        t = Mathf.Clamp01(t);

        switch (easingMode)
        {
            case EasingMode.Linear:
                return t;
            case EasingMode.SmoothStep:
                return Mathf.SmoothStep(0f, 1f, t);
            default:
                return Mathf.Clamp01(customCurve.Evaluate(t));
        }
    }

    private float GetPingPongTime()
    {
        float cycle = pingPong
            ? Mathf.PingPong(elapsed / duration, 1f)
            : Mathf.Repeat(elapsed / duration, 1f);

        return Mathf.Clamp01(cycle);
    }

    private void HandleShortcuts()
    {
        if (!enableShortcuts)
        {
            return;
        }

        if (WasSpacePressedThisFrame())
        {
            pathMode = pathMode == PathMode.LinearLerp ? PathMode.Bezier : PathMode.LinearLerp;
        }

        if (WasTabPressedThisFrame())
        {
            easingMode = easingMode == EasingMode.AnimationCurve
                ? EasingMode.Linear
                : (EasingMode)((int)easingMode + 1);
        }
    }

    private void RefreshPathLines()
    {
        if (!ArePointsReady() || pathRenderer == null || helperRenderer == null)
        {
            return;
        }

        int segments = pathMode == PathMode.Bezier ? 32 : 2;
        pathRenderer.positionCount = segments;

        for (int i = 0; i < segments; i++)
        {
            float t = segments == 1 ? 0f : i / (segments - 1f);
            Vector3 pathPoint = pathMode == PathMode.Bezier
                ? EvaluateBezier(t)
                : Vector3.Lerp(pointA.position, pointB.position, t);

            pathRenderer.SetPosition(i, pathPoint + Vector3.up * 0.05f);
        }

        helperRenderer.enabled = pathMode == PathMode.Bezier;
        helperRenderer.positionCount = 4;
        helperRenderer.SetPosition(0, pointA.position);
        helperRenderer.SetPosition(1, controlPointA.position);
        helperRenderer.SetPosition(2, controlPointB.position);
        helperRenderer.SetPosition(3, pointB.position);
    }

    private void UpdateOverlay(float rawT, float easedT)
    {
        if (progressFill != null)
        {
            RectTransform parent = progressFill.parent as RectTransform;
            float width = parent != null ? parent.rect.width * Mathf.Clamp01(rawT) : 0f;
            progressFill.sizeDelta = new Vector2(width, 0f);
        }

        if (statusLabel != null)
        {
            float visibleTime = rawT * duration;
            statusLabel.text =
                $"Trayecto: {GetPathLabel()}  |  Easing: {GetEasingLabel()}\n" +
                $"t bruto: {rawT:0.00}  |  t suavizado: {easedT:0.00}  |  Tiempo: {visibleTime:0.00}s / {duration:0.00}s\n" +
                "Posicion: Vector3.Lerp / Bezier  |  Rotacion: Quaternion.Slerp";
        }

        if (titleLabel != null)
        {
            titleLabel.text = "Interpolacion de movimiento y rotacion";
        }

        if (shortcutLabel != null)
        {
            shortcutLabel.enabled = enableShortcuts;
        }
    }

    private Vector3 EvaluateBezier(float t)
    {
        Vector3 p0 = pointA.position;
        Vector3 p1 = controlPointA.position;
        Vector3 p2 = controlPointB.position;
        Vector3 p3 = pointB.position;

        float oneMinusT = 1f - t;
        return
            oneMinusT * oneMinusT * oneMinusT * p0 +
            3f * oneMinusT * oneMinusT * t * p1 +
            3f * oneMinusT * t * t * p2 +
            t * t * t * p3;
    }

    private bool ArePointsReady()
    {
        return pointA != null && pointB != null && controlPointA != null && controlPointB != null;
    }

    private GameObject EnsurePrimitiveChild(
        Transform parent,
        string objectName,
        PrimitiveType primitiveType,
        Vector3 localPosition,
        Vector3 localEulerAngles,
        Vector3 localScale)
    {
        Transform existing = parent.Find(objectName);
        if (existing != null)
        {
            return existing.gameObject;
        }

        GameObject created = GameObject.CreatePrimitive(primitiveType);
        created.name = objectName;
        created.transform.SetParent(parent, false);
        created.transform.localPosition = localPosition;
        created.transform.localEulerAngles = localEulerAngles;
        created.transform.localScale = localScale;
        return created;
    }

    private Transform EnsureChildTransform(
        ref Transform target,
        Transform parent,
        string objectName,
        Vector3 localPosition,
        Vector3 localEulerAngles,
        Vector3 localScale)
    {
        if (target == null)
        {
            Transform existing = parent.Find(objectName);
            if (existing == null)
            {
                GameObject child = new GameObject(objectName);
                target = child.transform;
                target.SetParent(parent, false);
                target.localPosition = localPosition;
                target.localEulerAngles = localEulerAngles;
                target.localScale = localScale;
            }
            else
            {
                target = existing;
            }
        }

        return target;
    }

    private LineRenderer EnsureLineRenderer(
        ref LineRenderer target,
        string objectName,
        Color color,
        float width,
        int defaultPoints)
    {
        if (target == null)
        {
            Transform existing = generatedRoot.Find(objectName);
            if (existing == null)
            {
                GameObject lineObject = new GameObject(objectName, typeof(LineRenderer));
                lineObject.transform.SetParent(generatedRoot, false);
                target = lineObject.GetComponent<LineRenderer>();
            }
            else
            {
                target = existing.GetComponent<LineRenderer>();
            }
        }

        target.positionCount = defaultPoints;
        target.useWorldSpace = true;
        target.loop = false;
        target.widthMultiplier = width;
        target.numCornerVertices = 6;
        target.numCapVertices = 6;
        target.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        target.receiveShadows = false;

        if (runtimeLineMaterial == null)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit");
            if (shader == null)
            {
                shader = Shader.Find("Sprites/Default");
            }

            runtimeLineMaterial = new Material(shader)
            {
                hideFlags = HideFlags.HideAndDontSave
            };
        }

        target.sharedMaterial = runtimeLineMaterial;
        target.startColor = color;
        target.endColor = color;
        return target;
    }

    private T EnsureUiObject<T>(Transform parent, string objectName) where T : Component
    {
        Transform existing = parent.Find(objectName);
        if (existing != null)
        {
            return existing.GetComponent<T>();
        }

        GameObject created = new GameObject(objectName, typeof(RectTransform), typeof(T));
        created.transform.SetParent(parent, false);
        return created.GetComponent<T>();
    }

    private Text EnsureText(
        RectTransform parent,
        ref Text target,
        string objectName,
        string defaultText,
        int fontSize,
        FontStyle fontStyle,
        Vector2 anchoredPosition,
        Vector2 size)
    {
        if (target == null)
        {
            target = EnsureUiObject<Text>(parent, objectName);
        }

        RectTransform rect = target.rectTransform;
        rect.anchorMin = new Vector2(0f, 1f);
        rect.anchorMax = new Vector2(0f, 1f);
        rect.pivot = new Vector2(0f, 1f);
        rect.anchoredPosition = anchoredPosition;
        rect.sizeDelta = size;

        target.text = defaultText;
        target.font = GetBuiltinFont();
        target.fontSize = fontSize;
        target.fontStyle = fontStyle;
        target.alignment = TextAnchor.UpperLeft;
        target.horizontalOverflow = HorizontalWrapMode.Wrap;
        target.verticalOverflow = VerticalWrapMode.Overflow;
        target.color = Color.white;
        return target;
    }

    private Font GetBuiltinFont()
    {
        Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        if (font == null)
        {
            font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        }

        return font;
    }

    private string GetPathLabel()
    {
        return pathMode == PathMode.LinearLerp ? "Vector3.Lerp" : "Bezier";
    }

    private string GetEasingLabel()
    {
        switch (easingMode)
        {
            case EasingMode.Linear:
                return "Lineal";
            case EasingMode.SmoothStep:
                return "Mathf.SmoothStep";
            default:
                return "AnimationCurve";
        }
    }

#if ENABLE_INPUT_SYSTEM
    private static bool WasSpacePressedThisFrame()
    {
        Keyboard keyboard = Keyboard.current;
        return keyboard != null && keyboard.spaceKey.wasPressedThisFrame;
    }

    private static bool WasTabPressedThisFrame()
    {
        Keyboard keyboard = Keyboard.current;
        return keyboard != null && keyboard.tabKey.wasPressedThisFrame;
    }
#else
    private static bool WasSpacePressedThisFrame()
    {
        return Input.GetKeyDown(KeyCode.Space);
    }

    private static bool WasTabPressedThisFrame()
    {
        return Input.GetKeyDown(KeyCode.Tab);
    }
#endif
}
