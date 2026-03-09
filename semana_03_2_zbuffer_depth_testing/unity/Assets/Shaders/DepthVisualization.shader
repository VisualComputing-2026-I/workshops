Shader "Custom/DepthVisualization"
{
    // =========================================================================
    // Shader que visualiza el depth buffer en escala de grises.
    // Permite alternar entre profundidad no-lineal (nativa del GPU)
    // y profundidad linealizada, controlado desde el material.
    // =========================================================================
    Properties
    {
        [Toggle] _LinearMode ("Modo Lineal", Float) = 0
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" }
        LOD 100

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma shader_feature _LINEARMODE_ON
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
            };

            struct v2f
            {
                float4 pos      : SV_POSITION;
                float  depth    : TEXCOORD0;
                float  linearZ  : TEXCOORD1;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);

                // Profundidad no-lineal tal como la ve el GPU [0,1]
                o.depth = o.pos.z / o.pos.w;
                // En plataformas donde Z va de -1 a 1, remap a 0..1
                #if !defined(UNITY_REVERSED_Z)
                    o.depth = o.depth * 0.5 + 0.5;
                #endif

                // Profundidad lineal en unidades del mundo
                float4 viewPos = mul(UNITY_MATRIX_MV, v.vertex);
                o.linearZ = -viewPos.z; // distancia positiva desde la camara

                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                float d;

                #ifdef _LINEARMODE_ON
                    // Linealizar usando near/far de la camara
                    d = (i.linearZ - _ProjectionParams.y) /
                        (_ProjectionParams.z - _ProjectionParams.y);
                    d = saturate(d);
                #else
                    // Profundidad nativa no-lineal
                    d = i.depth;
                    // En reversed-Z (Unity default), invertir para que
                    // cercano = oscuro, lejano = claro
                    #if defined(UNITY_REVERSED_Z)
                        d = 1.0 - d;
                    #endif
                #endif

                return fixed4(d, d, d, 1.0);
            }
            ENDCG
        }
    }

    FallBack "Diffuse"
}
