using UnityEngine;

namespace ProceduralModeling
{
    public class ProceduralSceneGenerator : MonoBehaviour
    {
        [Header("Automatic Generation")]
        [SerializeField] private bool generateOnStart = true;
        [SerializeField] private bool clearPreviousChildren = true;
        [SerializeField] private bool repositionMainCamera = true;
        [SerializeField] private bool attachCameraController = true;

        [Header("Cube Grid")]
        [SerializeField, Min(1)] private int cubeRows = 4;
        [SerializeField, Min(1)] private int cubeColumns = 5;
        [SerializeField, Min(0.5f)] private float cubeSpacing = 1.35f;
        [SerializeField] private Vector3 cubeGridOrigin = new Vector3(-4.5f, 0f, -2f);

        [Header("Cylinder Spiral")]
        [SerializeField, Min(3)] private int cylinderCount = 16;
        [SerializeField, Min(0.05f)] private float spiralStartRadius = 0.6f;
        [SerializeField, Min(0.01f)] private float spiralRadiusStep = 0.18f;
        [SerializeField, Min(0.05f)] private float spiralHeightStep = 0.24f;
        [SerializeField] private float spiralAngleStep = 32f;
        [SerializeField] private Vector3 spiralOrigin = new Vector3(0.5f, 0f, -0.5f);

        [Header("Fractal Pyramid")]
        [SerializeField, Range(0, 3)] private int fractalDepth = 2;
        [SerializeField, Min(0.2f)] private float fractalBaseScale = 1.1f;
        [SerializeField] private Vector3 fractalOrigin = new Vector3(4.5f, 0.6f, 1f);

        [Header("Custom Mesh")]
        [SerializeField] private Vector3 customMeshOrigin = new Vector3(0f, 0f, 4.25f);
        [SerializeField] private Vector3 customMeshRotation = new Vector3(0f, 28f, 0f);
        [SerializeField] private Vector3 customMeshScale = new Vector3(1.4f, 1.4f, 1.4f);

        private bool generated;

        private void Start()
        {
            if (!generateOnStart || generated)
            {
                return;
            }

            GenerateDemo();
        }

        [ContextMenu("Generate Demo")]
        public void GenerateDemo()
        {
            if (clearPreviousChildren)
            {
                ClearGeneratedObjects();
            }

            if (repositionMainCamera)
            {
                PositionMainCamera();
            }

            CreateCubeGrid();
            CreateCylinderSpiral();
            CreateFractalPyramid();
            CreateCustomMeshObject();
            generated = true;
        }

        [ContextMenu("Clear Generated Objects")]
        public void ClearGeneratedObjects()
        {
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                Transform child = transform.GetChild(i);

                if (Application.isPlaying)
                {
                    Destroy(child.gameObject);
                }
                else
                {
                    DestroyImmediate(child.gameObject);
                }
            }

            generated = false;
        }

        private void CreateCubeGrid()
        {
            Transform section = CreateSection("Cube Grid");
            int total = Mathf.Max(1, cubeRows * cubeColumns - 1);
            int index = 0;

            Vector3 startOffset = new Vector3(
                -((cubeColumns - 1) * cubeSpacing) * 0.5f,
                0f,
                -((cubeRows - 1) * cubeSpacing) * 0.5f);

            for (int row = 0; row < cubeRows; row++)
            {
                for (int column = 0; column < cubeColumns; column++)
                {
                    GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    cube.name = $"GridCube_{row}_{column}";
                    cube.transform.SetParent(section, false);

                    float heightScale = 0.75f + 0.35f * Mathf.Sin((row + column) * 0.75f);
                    cube.transform.localPosition = cubeGridOrigin + startOffset + new Vector3(column * cubeSpacing, 0f, row * cubeSpacing);
                    cube.transform.localRotation = Quaternion.Euler(row * 7f, column * 14f, 0f);
                    cube.transform.localScale = new Vector3(1f, 1f + heightScale, 1f);

                    Color color = Color.Lerp(new Color(0.18f, 0.56f, 0.86f), new Color(0.87f, 0.95f, 1f), index / (float)total);
                    ApplyColor(cube, color);
                    index++;
                }
            }
        }

        private void CreateCylinderSpiral()
        {
            Transform section = CreateSection("Cylinder Spiral");

            for (int i = 0; i < cylinderCount; i++)
            {
                GameObject cylinder = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                cylinder.name = $"SpiralCylinder_{i}";
                cylinder.transform.SetParent(section, false);

                float angle = spiralAngleStep * i;
                float angleInRadians = angle * Mathf.Deg2Rad;
                float radius = spiralStartRadius + spiralRadiusStep * i;

                cylinder.transform.localPosition = spiralOrigin + new Vector3(
                    Mathf.Cos(angleInRadians) * radius,
                    i * spiralHeightStep,
                    Mathf.Sin(angleInRadians) * radius);

                cylinder.transform.localRotation = Quaternion.Euler(0f, angle, 0f);
                cylinder.transform.localScale = new Vector3(0.45f, 0.35f + i * 0.03f, 0.45f);

                Color color = Color.Lerp(new Color(0.95f, 0.58f, 0.18f), new Color(0.6f, 0.17f, 0.12f), i / Mathf.Max(1f, cylinderCount - 1f));
                ApplyColor(cylinder, color);
            }
        }

        private void CreateFractalPyramid()
        {
            Transform section = CreateSection("Fractal Pyramid");
            CreateFractalNode(section, fractalOrigin, fractalBaseScale, fractalDepth);
        }

        private void CreateFractalNode(Transform parent, Vector3 center, float scale, int depth)
        {
            GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            sphere.name = $"FractalSphere_Depth_{depth}";
            sphere.transform.SetParent(parent, false);
            sphere.transform.localPosition = center;
            sphere.transform.localRotation = Quaternion.identity;
            sphere.transform.localScale = Vector3.one * scale;

            float colorLerp = fractalDepth == 0 ? 1f : depth / (float)fractalDepth;
            ApplyColor(sphere, Color.Lerp(new Color(0.2f, 0.78f, 0.48f), new Color(0.9f, 1f, 0.72f), colorLerp));

            if (depth <= 0)
            {
                return;
            }

            float childScale = scale * 0.55f;
            float offset = scale * 0.7f;

            Vector3[] offsets =
            {
                new Vector3(-offset, 0f, -offset),
                new Vector3(offset, 0f, -offset),
                new Vector3(offset, 0f, offset),
                new Vector3(-offset, 0f, offset),
                new Vector3(0f, offset * 1.35f, 0f)
            };

            for (int i = 0; i < offsets.Length; i++)
            {
                CreateFractalNode(parent, center + offsets[i], childScale, depth - 1);
            }
        }

        private void CreateCustomMeshObject()
        {
            GameObject meshObject = new GameObject("Custom Pyramid Mesh");
            meshObject.transform.SetParent(transform, false);
            meshObject.transform.localPosition = customMeshOrigin;
            meshObject.transform.localRotation = Quaternion.Euler(customMeshRotation);
            meshObject.transform.localScale = customMeshScale;

            MeshFilter meshFilter = meshObject.AddComponent<MeshFilter>();
            meshFilter.sharedMesh = ProceduralMeshFactory.CreatePyramidMesh(2.5f, 2f);

            MeshRenderer meshRenderer = meshObject.AddComponent<MeshRenderer>();
            Material material = CreateMaterial(new Color(0.81f, 0.24f, 0.31f));
            if (material != null)
            {
                meshRenderer.sharedMaterial = material;
            }
        }

        private Transform CreateSection(string sectionName)
        {
            GameObject section = new GameObject(sectionName);
            section.transform.SetParent(transform, false);
            return section.transform;
        }

        private void PositionMainCamera()
        {
            Camera mainCamera = Camera.main;
            if (mainCamera == null)
            {
                GameObject cameraObject = new GameObject("Main Camera");
                cameraObject.tag = "MainCamera";
                mainCamera = cameraObject.AddComponent<Camera>();
            }

            mainCamera.transform.position = new Vector3(0f, 5.5f, -14f);
            mainCamera.transform.rotation = Quaternion.Euler(18f, 0f, 0f);

            if (!attachCameraController)
            {
                return;
            }

            if (mainCamera.GetComponent<ProceduralCameraController>() == null)
            {
                mainCamera.gameObject.AddComponent<ProceduralCameraController>();
            }
        }

        private void ApplyColor(GameObject target, Color color)
        {
            Renderer renderer = target.GetComponent<Renderer>();
            if (renderer == null)
            {
                return;
            }

            Material material = CreateMaterial(color);
            if (material != null)
            {
                renderer.sharedMaterial = material;
            }
        }

        private Material CreateMaterial(Color color)
        {
            string[] shaderNames =
            {
                "Universal Render Pipeline/Lit",
                "Universal Render Pipeline/Simple Lit",
                "Standard"
            };

            for (int i = 0; i < shaderNames.Length; i++)
            {
                Shader shader = Shader.Find(shaderNames[i]);
                if (shader == null)
                {
                    continue;
                }

                Material material = new Material(shader)
                {
                    color = color
                };

                return material;
            }

            return null;
        }
    }
}
