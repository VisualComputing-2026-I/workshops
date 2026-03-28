using UnityEngine;

namespace ProceduralModeling
{
    public static class ProceduralMeshFactory
    {
        public static Mesh CreatePyramidMesh(float baseSize, float height)
        {
            float halfBase = baseSize * 0.5f;

            Vector3[] vertices =
            {
                new Vector3(-halfBase, 0f, -halfBase),
                new Vector3(halfBase, 0f, -halfBase),
                new Vector3(halfBase, 0f, halfBase),
                new Vector3(-halfBase, 0f, halfBase),
                new Vector3(0f, height, 0f)
            };

            int[] triangles =
            {
                0, 2, 1,
                0, 3, 2,
                0, 1, 4,
                1, 2, 4,
                2, 3, 4,
                3, 0, 4
            };

            Vector2[] uv =
            {
                new Vector2(0f, 0f),
                new Vector2(1f, 0f),
                new Vector2(1f, 1f),
                new Vector2(0f, 1f),
                new Vector2(0.5f, 1f)
            };

            Mesh mesh = new Mesh
            {
                name = "ProceduralPyramidMesh"
            };

            mesh.vertices = vertices;
            mesh.triangles = triangles;
            mesh.uv = uv;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();

            return mesh;
        }
    }
}
