Shader "Custom/VectorVisualization"
{
    // =========================================================================
    // Shader de debug que visualiza los vectores usados en iluminacion.
    // Mapea los vectores del rango [-1, 1] al rango [0, 1] para visualizacion RGB.
    //
    // Modos:
    //   0 = Normal (N)
    //   1 = Light direction (L)
    //   2 = View direction (V)
    //   3 = Reflection vector (R)
    //   4 = Half vector (H)
    // =========================================================================
    Properties
    {
        [KeywordEnum(Normal, LightDir, ViewDir, Reflect, HalfVector)]
        _VectorMode ("Vector Mode", Float) = 0
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" }
        LOD 100

        Pass
        {
            Tags { "LightMode"="ForwardBase" }

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile _VECTORMODE_NORMAL _VECTORMODE_LIGHTDIR _VECTORMODE_VIEWDIR _VECTORMODE_REFLECT _VECTORMODE_HALFVECTOR
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float3 worldNormal : TEXCOORD0;
                float3 worldPos : TEXCOORD1;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.worldNormal = UnityObjectToWorldNormal(v.normal);
                o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                float3 N = normalize(i.worldNormal);
                float3 L = normalize(_WorldSpaceLightPos0.xyz);
                float3 V = normalize(_WorldSpaceCameraPos - i.worldPos);
                float3 R = reflect(-L, N);
                float3 H = normalize(L + V);

                float3 vectorToShow;

                #if defined(_VECTORMODE_NORMAL)
                    vectorToShow = N;
                #elif defined(_VECTORMODE_LIGHTDIR)
                    vectorToShow = L;
                #elif defined(_VECTORMODE_VIEWDIR)
                    vectorToShow = V;
                #elif defined(_VECTORMODE_REFLECT)
                    vectorToShow = R;
                #elif defined(_VECTORMODE_HALFVECTOR)
                    vectorToShow = H;
                #else
                    vectorToShow = N;
                #endif

                // Mapear de [-1, 1] a [0, 1] para visualizacion RGB
                float3 color = vectorToShow * 0.5 + 0.5;

                return fixed4(color, 1.0);
            }
            ENDCG
        }
    }

    FallBack "Diffuse"
}
