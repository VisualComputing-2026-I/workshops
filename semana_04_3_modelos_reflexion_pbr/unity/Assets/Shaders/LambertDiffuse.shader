Shader "Custom/LambertDiffuse"
{
    // =========================================================================
    // Shader que implementa el modelo de iluminacion Lambertiano (difuso).
    // Ecuacion: I_diffuse = I_light * k_d * max(N . L, 0)
    // =========================================================================
    Properties
    {
        _DiffuseColor ("Diffuse Color", Color) = (0.8, 0.2, 0.2, 1)
        _AmbientColor ("Ambient Color", Color) = (0.1, 0.1, 0.15, 1)
        _LightIntensity ("Light Intensity", Range(0, 3)) = 1.0
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
            #pragma multi_compile_fwdbase
            #include "UnityCG.cginc"
            #include "Lighting.cginc"

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

            fixed4 _DiffuseColor;
            fixed4 _AmbientColor;
            float _LightIntensity;

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
                // Normalizar vectores
                float3 N = normalize(i.worldNormal);
                float3 L = normalize(_WorldSpaceLightPos0.xyz);

                // Componente ambiente
                fixed3 ambient = _AmbientColor.rgb * _DiffuseColor.rgb;

                // Componente difusa (Lambert): I_d = k_d * max(N . L, 0)
                float NdotL = max(dot(N, L), 0.0);
                fixed3 diffuse = _LightColor0.rgb * _DiffuseColor.rgb * NdotL * _LightIntensity;

                // Color final
                fixed3 finalColor = ambient + diffuse;
                return fixed4(finalColor, 1.0);
            }
            ENDCG
        }
    }

    FallBack "Diffuse"
}
