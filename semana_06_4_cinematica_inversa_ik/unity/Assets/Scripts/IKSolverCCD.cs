using UnityEngine;

public class IKSolverCCD : MonoBehaviour
{
    [Header("Auto Setup")]
    public bool autoSetupOnAwake = true;
    [Range(3, 8)] public int segmentCount = 4;
    [Min(0.1f)] public float segmentLength = 1.0f;
    [Min(0.02f)] public float segmentThickness = 0.18f;
    public bool useZAxisChain = false;
    public Vector3 targetOffsetFromRoot = new Vector3(1.6f, 1.6f, 1.4f);

    [Header("IK Solver")]
    public int iterations = 10;
    public float tolerance = 0.01f;
    [Range(1f, 45f)] public float maxDegreesPerStep = 12f;

    [Header("Target Controls")]
    public float targetMoveSpeed = 2.5f;

    private Transform target;
    private Transform[] joints;
    private Quaternion[] initialRotations;
    private Vector3 initialTargetPosition;
    private bool targetOutOfReach;
    private LineRenderer lineToTarget;

    private const string GeneratedRootName = "__IK_GENERATED_CHAIN";
    private const string GeneratedTargetName = "IK_Target";

    void Awake()
    {
        if (autoSetupOnAwake)
        {
            BuildOrRebuildSetup();
        }
    }

    [ContextMenu("Build/Rebuild IK Setup")]
    public void BuildOrRebuildSetup()
    {
        CleanupGeneratedObjects();

        BuildChain();
        BuildTarget();
        SetupLineRenderer();

        CacheInitialPose();
    }

    private void BuildChain()
    {
        Vector3 axis = GetChainAxisLocal();
        GameObject generatedRoot = new GameObject(GeneratedRootName);
        generatedRoot.transform.SetParent(transform, false);

        joints = new Transform[segmentCount];

        Transform parent = generatedRoot.transform;
        for (int i = 0; i < segmentCount; i++)
        {
            string segmentName = i == 0 ? "Base" : (i == segmentCount - 1 ? "Mano" : "Segmento_" + i);
            GameObject segment = new GameObject(segmentName);
            Transform segmentTransform = segment.transform;
            segmentTransform.SetParent(parent, false);
            segmentTransform.localPosition = i == 0 ? Vector3.zero : axis * segmentLength;
            segmentTransform.localRotation = Quaternion.identity;

            CreateSegmentVisual(segmentTransform, axis);

            joints[i] = segmentTransform;
            parent = segmentTransform;
        }
    }

    private void CreateSegmentVisual(Transform segmentTransform, Vector3 axis)
    {
        GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        visual.name = "Visual";
        visual.transform.SetParent(segmentTransform, false);

        // Cylinder default axis is +Y. Rotate to align if we choose +Z chain.
        if (useZAxisChain)
        {
            visual.transform.localRotation = Quaternion.Euler(90f, 0f, 0f);
        }

        visual.transform.localPosition = axis * (segmentLength * 0.5f);
        visual.transform.localScale = new Vector3(segmentThickness, segmentLength * 0.5f, segmentThickness);
    }

    private void BuildTarget()
    {
        GameObject targetObject = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        targetObject.name = GeneratedTargetName;
        targetObject.transform.position = transform.position + targetOffsetFromRoot;
        targetObject.transform.localScale = Vector3.one * 0.3f;

        Renderer rendererRef = targetObject.GetComponent<Renderer>();
        if (rendererRef != null)
        {
            rendererRef.material.color = new Color(1f, 0.45f, 0.1f);
        }

        target = targetObject.transform;
        initialTargetPosition = target.position;
    }

    private void SetupLineRenderer()
    {
        lineToTarget = GetComponent<LineRenderer>();
        if (lineToTarget == null)
        {
            lineToTarget = gameObject.AddComponent<LineRenderer>();
        }

        lineToTarget.positionCount = 2;
        lineToTarget.material = new Material(Shader.Find("Sprites/Default"));
        lineToTarget.widthMultiplier = 0.04f;
        lineToTarget.startColor = Color.red;
        lineToTarget.endColor = Color.yellow;
        lineToTarget.useWorldSpace = true;
    }

    private void CacheInitialPose()
    {
        if (joints == null || joints.Length == 0)
        {
            return;
        }

        initialRotations = new Quaternion[joints.Length];
        for (int i = 0; i < joints.Length; i++)
        {
            initialRotations[i] = joints[i].localRotation;
        }
    }

    private void CleanupGeneratedObjects()
    {
        Transform generatedRoot = transform.Find(GeneratedRootName);
        if (generatedRoot != null)
        {
            DestroyImmediate(generatedRoot.gameObject);
        }

        GameObject previousTarget = GameObject.Find(GeneratedTargetName);
        if (previousTarget != null)
        {
            DestroyImmediate(previousTarget);
        }
    }

    void Update()
    {
        if (joints == null || joints.Length == 0 || target == null)
        {
            return;
        }

        MoveTarget();
        SolveIK();
        UpdateDebugAndLine();
    }

    private void SolveIK()
    {
        float maxReach = joints.Length * segmentLength;
        float rootToTarget = Vector3.Distance(joints[0].position, target.position);
        targetOutOfReach = rootToTarget > maxReach;

        for (int iter = 0; iter < iterations; iter++)
        {
            Vector3 endPos = GetEndEffectorPosition();
            if (Vector3.Distance(endPos, target.position) < tolerance)
            {
                return;
            }

            for (int i = joints.Length - 1; i >= 0; i--)
            {
                Transform currentJoint = joints[i];

                Vector3 toEndEffector = GetEndEffectorPosition() - currentJoint.position;
                Vector3 toTarget = target.position - currentJoint.position;
                if (toEndEffector.sqrMagnitude < 0.000001f || toTarget.sqrMagnitude < 0.000001f)
                {
                    continue;
                }

                Quaternion deltaRotation = Quaternion.FromToRotation(toEndEffector.normalized, toTarget.normalized);
                deltaRotation.ToAngleAxis(out float angle, out Vector3 axis);
                if (angle > 180f)
                {
                    angle -= 360f;
                }

                float clampedAngle = Mathf.Clamp(angle, -maxDegreesPerStep, maxDegreesPerStep);
                Quaternion incrementalRotation = Quaternion.AngleAxis(clampedAngle, axis);
                currentJoint.rotation = incrementalRotation * currentJoint.rotation;

                if (Vector3.Distance(GetEndEffectorPosition(), target.position) < tolerance)
                {
                    return;
                }
            }
        }
    }

    private Vector3 GetEndEffectorPosition()
    {
        Transform lastJoint = joints[joints.Length - 1];
        Vector3 axis = useZAxisChain ? lastJoint.forward : lastJoint.up;
        return lastJoint.position + axis * segmentLength;
    }

    private Vector3 GetChainAxisLocal()
    {
        return useZAxisChain ? Vector3.forward : Vector3.up;
    }

    private void UpdateDebugAndLine()
    {
        Vector3 endPos = GetEndEffectorPosition();
        Debug.DrawLine(endPos, target.position, Color.red);
        Debug.DrawRay(joints[joints.Length - 1].position, joints[joints.Length - 1].forward * 1.5f, Color.green);

        if (lineToTarget != null)
        {
            lineToTarget.SetPosition(0, endPos);
            lineToTarget.SetPosition(1, target.position);
        }
    }

    private void MoveTarget()
    {
        float speed = targetMoveSpeed * Time.deltaTime;
        if (Input.GetKey(KeyCode.UpArrow))
            target.position += Vector3.up * speed;
        if (Input.GetKey(KeyCode.DownArrow))
            target.position += Vector3.down * speed;
        if (Input.GetKey(KeyCode.RightArrow))
            target.position += Vector3.right * speed;
        if (Input.GetKey(KeyCode.LeftArrow))
            target.position += Vector3.left * speed;
        if (Input.GetKey(KeyCode.W))
            target.position += Vector3.forward * speed;
        if (Input.GetKey(KeyCode.S))
            target.position += Vector3.back * speed;
    }

    private void OnGUI()
    {
        GUILayout.BeginArea(new Rect(15, 15, 370, 250), GUI.skin.box);
        GUILayout.Label("IK CCD Demo (Auto Setup)");
        GUILayout.Label("Mover target: Flechas + W/S");
        GUILayout.Label(targetOutOfReach ? "Estado: TARGET FUERA DE ALCANCE" : "Estado: target alcanzable");

        if (GUILayout.Button("Reset Pose", GUILayout.Height(28)))
        {
            ResetPose();
        }

        GUILayout.Space(8);
        GUILayout.Label("Bonus: cambiar parametros y reconstruir");
        GUILayout.Label("Segmentos: " + segmentCount);
        segmentCount = Mathf.RoundToInt(GUILayout.HorizontalSlider(segmentCount, 3, 8));
        GUILayout.Label("Largo segmento: " + segmentLength.ToString("F2"));
        segmentLength = GUILayout.HorizontalSlider(segmentLength, 0.3f, 2.0f);

        if (GUILayout.Button("Rebuild Setup", GUILayout.Height(26)))
        {
            BuildOrRebuildSetup();
        }

        GUILayout.EndArea();
    }

    public void ResetPose()
    {
        if (joints == null || initialRotations == null)
        {
            return;
        }

        for (int i = 0; i < joints.Length; i++)
        {
            joints[i].localRotation = initialRotations[i];
        }

        if (target != null)
        {
            target.position = initialTargetPosition;
        }
    }
}
