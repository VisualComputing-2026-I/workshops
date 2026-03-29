Shader "Custom/IlluminationComponents"
{
    // =========================================================================
    // Shader que permite visualizar componentes individuales de iluminacion.
    // Util para entender la contribucion de cada termino.
    //
    // Modos:
    //   Full    = Ambient + Diffuse + Specular
    //   Ambient = Solo componente ambiente
    //   Diffuse = Solo componente difusa
    //   Specular = Solo componente especular
    // =========================================================================
    Properties
    {
        _DiffuseColor ("Diffuse Color", Color) = (0.8, 0.2, 0.2, 1)
        _SpecularColor ("Specular Color", Color) = (1, 1, 1, 1)
        _AmbientColor ("Ambient Color", Color) = (0.1, 0.1, 0.15, 1)
        _Shininess ("Shininess", Range(1, 256)) = 32
        _LightIntensity ("Light Intensity", Range(0, 3)) = 1.0

        [KeywordEnum(Full, Ambient, Diffuse, Specular)]
        _ViewMode ("View Mode", Float) = 0
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
            #pragma multi_compile _VIEWMODE_FULL _VIEWMODE_AMBIENT _VIEWMODE_DIFFUSE _VIEWMODE_SPECULAR
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
                float3 N = normalize(i.worldNormal);
                float3 L = normalize(_WorldSpaceLightPos0.xyz);
                float3 V = normalize(_WorldSpaceCameraPos - i.worldPos);
                float3 H = normalize(L + V);

                // Calcular todos los componentes
                fixed3 ambient = _AmbientColor.rgb * _DiffuseColor.rgb;

                float NdotL = max(dot(N, L), 0.0);
                fixed3 diffuse = _LightColor0.rgb * _DiffuseColor.rgb * NdotL * _LightIntensity;

                float NdotH = max(dot(N, H), 0.0);
                float specularFactor = pow(NdotH, _Shininess);
                fixed3 specular = fixed3(0, 0, 0);
                if (NdotL > 0.0)
                {
                    specular = _LightColor0.rgb * _SpecularColor.rgb * specularFactor * _LightIntensity;
                }

                // Seleccionar que mostrar segun el modo
                fixed3 finalColor;

                #if defined(_VIEWMODE_FULL)
                    finalColor = ambient + diffuse + specular;
                #elif defined(_VIEWMODE_AMBIENT)
                    finalColor = ambient;
                #elif defined(_VIEWMODE_DIFFUSE)
                    finalColor = diffuse;
                #elif defined(_VIEWMODE_SPECULAR)
                    finalColor = specular;
                #else
                    finalColor = ambient + diffuse + specular;
                #endif

                return fixed4(finalColor, 1.0);
            }
            ENDCG
        }
    }

    FallBack "Specular"
}
