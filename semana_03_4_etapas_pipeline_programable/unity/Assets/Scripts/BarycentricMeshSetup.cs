using UnityEngine;

[RequireComponent(typeof(MeshFilter))]
public class BarycentricMeshSetup : MonoBehaviour
{
    void Start()
    {
        MeshFilter mf      = GetComponent<MeshFilter>();
        Mesh       srcMesh = mf.mesh;
        int[]      tris    = srcMesh.triangles;
        int        triCount = tris.Length; 

        Vector3[] newVerts   = new Vector3[triCount];
        Vector3[] newNormals = new Vector3[triCount];
        Vector2[] newUVs     = new Vector2[triCount];
        int[]     newTris    = new int[triCount];

        Vector3[] srcVerts   = srcMesh.vertices;
        Vector3[] srcNormals = srcMesh.normals;
        Vector2[] srcUVs     = srcMesh.uv;

        for (int i = 0; i < triCount; i++)
        {
            newVerts  [i] = srcVerts  [tris[i]];
            newNormals[i] = srcNormals[tris[i]];
            newUVs    [i] = srcUVs    [tris[i]];
            newTris   [i] = i;
        }

    
        Vector2[] baryUV = new Vector2[triCount];
        Vector2[] baryPattern = { new Vector2(1, 0), new Vector2(0, 1), new Vector2(0, 0) };

        for (int i = 0; i < triCount; i++)
        {
            baryUV[i] = baryPattern[i % 3];
        }

        Mesh newMesh      = new Mesh();
        newMesh.name      = srcMesh.name + "_Bary";
        newMesh.vertices  = newVerts;
        newMesh.normals   = newNormals;
        newMesh.uv        = newUVs;
        newMesh.uv2       = baryUV;   // TEXCOORD1 = coordenadas baricéntricas
        newMesh.triangles = newTris;
        newMesh.RecalculateBounds();

        mf.mesh = newMesh;

        Debug.Log($"[BarycentricMeshSetup] '{gameObject.name}': " +
                  $"{srcMesh.triangles.Length / 3} triángulos procesados. " +
                  $"Coordenadas baricéntricas listas para wireframe.");
    }
}
