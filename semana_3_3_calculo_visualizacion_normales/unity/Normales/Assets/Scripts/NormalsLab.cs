using UnityEngine;

[RequireComponent(typeof(MeshFilter))]
public class NormalsLab : MonoBehaviour
{
    public float normalLength = 0.08f;
    public bool drawImportedNormals = true;
    public bool drawManualNormals = true;
    public bool drawCurrentMeshNormals = false;

    private MeshFilter mf;

    void Awake()
    {
        mf = GetComponent<MeshFilter>();
    }

    Mesh GetMesh()
    {
        // En Play usa instancia (mesh), en Edit usa sharedMesh.
        return Application.isPlaying ? mf.mesh : mf.sharedMesh;
    }

    [ContextMenu("Recalculate Normals (Unity)")]
    void RecalculateWithUnity()
    {
        Mesh mesh = GetMesh();
        if (mesh == null) return;
        mesh.RecalculateNormals();
    }

    [ContextMenu("Apply Manual Normals")]
    void ApplyManualNormals()
    {
        Mesh mesh = GetMesh();
        if (mesh == null) return;
        mesh.normals = CalculateManualNormals(mesh);
    }

    public static Vector3[] CalculateManualNormals(Mesh mesh)
    {
        Vector3[] vertices = mesh.vertices;
        int[] triangles = mesh.triangles;
        Vector3[] normals = new Vector3[vertices.Length];

        for (int i = 0; i < triangles.Length; i += 3)
        {
            int i0 = triangles[i];
            int i1 = triangles[i + 1];
            int i2 = triangles[i + 2];

            Vector3 e1 = vertices[i1] - vertices[i0];
            Vector3 e2 = vertices[i2] - vertices[i0];
            Vector3 faceNormal = Vector3.Cross(e1, e2); // Pondera por area del triangulo

            normals[i0] += faceNormal;
            normals[i1] += faceNormal;
            normals[i2] += faceNormal;
        }

        for (int i = 0; i < normals.Length; i++)
            normals[i] = normals[i].normalized;

        return normals;
    }

    void OnDrawGizmosSelected()
    {
        if (mf == null) mf = GetComponent<MeshFilter>();
        Mesh mesh = GetMesh();
        if (mesh == null) return;

        Vector3[] vertices = mesh.vertices;
        Vector3[] imported = mesh.normals;
        Vector3[] manual = CalculateManualNormals(mesh);

        for (int i = 0; i < vertices.Length; i++)
        {
            Vector3 wp = transform.TransformPoint(vertices[i]);

            if (drawImportedNormals && i < imported.Length)
            {
                Gizmos.color = Color.cyan;
                Vector3 wn = transform.TransformDirection(imported[i]).normalized;
                Gizmos.DrawLine(wp, wp + wn * normalLength);
            }

            if (drawManualNormals && i < manual.Length)
            {
                Gizmos.color = Color.yellow;
                Vector3 wn = transform.TransformDirection(manual[i]).normalized;
                Gizmos.DrawLine(wp, wp + wn * normalLength * 0.9f);
            }
        }
    }
}
