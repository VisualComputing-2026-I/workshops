Shader "Custom/BlinnPhongSpecular"
{
    // =========================================================================
    // Shader que implementa el modelo de iluminacion Blinn-Phong.
    // Optimizacion del modelo Phong usando el half vector en lugar del vector
    // de reflexion.
    //
    // Ecuaciones:
    //   I_diffuse  = k_d * max(N . L, 0)
    //   I_specular = k_s * max(N . H, 0)^shininess
    //   H = normalize(L + V)  (half vector)
    //
    // Ventajas sobre Phong clasico:
    //   - Mas eficiente (no necesita calcular reflect)
    //   - Mas realista para materiales brillantes
    //   - Highlight mas suave y natural
    // =========================================================================
    Properties
    {
        _DiffuseColor ("Diffuse Color", Color) = (0.8, 0.2, 0.2, 1)
        _SpecularColor ("Specular Color", Color) = (1, 1, 1, 1)
        _AmbientColor ("Ambient Color", Color) = (0.1, 0.1, 0.15, 1)
        _Shininess ("Shininess", Range(1, 256)) = 32
        _LightIntensity ("Light Intensity", Range(0, 3)) = 1.0
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" }
        LOD 200

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
            fixed4 _SpecularColor;
            fixed4 _AmbientColor;
            float _Shininess;
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
                float3 V = normalize(_WorldSpaceCameraPos - i.worldPos);

                // Componente ambiente
                fixed3 ambient = _AmbientColor.rgb * _DiffuseColor.rgb;

                // Componente difusa (Lambert)
                float NdotL = max(dot(N, L), 0.0);
                fixed3 diffuse = _LightColor0.rgb * _DiffuseColor.rgb * NdotL * _LightIntensity;

                // Componente especular (Blinn-Phong)
                // H = normalize(L + V) - half vector
                float3 H = normalize(L + V);
                float NdotH = max(dot(N, H), 0.0);
                float specularFactor = pow(NdotH, _Shininess);

                // Solo calcular especular si hay luz difusa
                fixed3 specular = fixed3(0, 0, 0);
                if (NdotL > 0.0)
                {
                    specular = _LightColor0.rgb * _SpecularColor.rgb * specularFactor * _LightIntensity;
                }

                // Color final
                fixed3 finalColor = ambient + diffuse + specular;
                return fixed4(finalColor, 1.0);
            }
            ENDCG
        }
    }

    FallBack "Specular"
}
