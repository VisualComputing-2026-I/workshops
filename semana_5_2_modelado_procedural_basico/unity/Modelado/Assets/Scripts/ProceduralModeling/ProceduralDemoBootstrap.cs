using UnityEngine;

namespace ProceduralModeling
{
    public static class ProceduralDemoBootstrap
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void CreateGeneratorIfMissing()
        {
            if (Object.FindFirstObjectByType<ProceduralSceneGenerator>() != null)
            {
                return;
            }

            GameObject root = new GameObject("Procedural Modeling Demo");
            root.AddComponent<ProceduralSceneGenerator>();
        }
    }
}
