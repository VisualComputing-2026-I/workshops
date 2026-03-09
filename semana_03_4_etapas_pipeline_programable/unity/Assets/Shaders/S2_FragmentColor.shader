Shader "Taller/S2_FragmentColor"
{
    Properties
    {
        _MainTex    ("Textura",     2D)    = "white" {}
        _TintColor  ("Color Tinte", Color) = (1,1,1,1)

        _LightDir   ("Dirección de Luz (World)", Vector) = (1, 1, 0.5, 0)
        _LightColor ("Color de Luz",  Color) = (1, 0.95, 0.8, 1)
        _Ambient    ("Luz Ambiental", Color) = (0.1, 0.1, 0.2, 1)

        [KeywordEnum(LAMBERT, TEXTURE, GRADIENT, CHECKER, RINGS)]
        _FragMode ("Modo Fragment", Float) = 0

        _GradColorA ("Gradiente Color A", Color) = (0.1, 0.2, 0.9, 1)
        _GradColorB ("Gradiente Color B", Color) = (0.9, 0.1, 0.3, 1)

        _CheckScale ("Checker Escala", Range(2, 20)) = 8

        _RingCount  ("Anillos Cantidad", Range(1, 15)) = 6
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }

        Pass
        {
            Name "S2_Forward"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 4.5
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _MainTex_ST;
                float4 _TintColor;
                float4 _LightDir;
                float4 _LightColor;
                float4 _Ambient;
                float  _FragMode;
                float4 _GradColorA;
                float4 _GradColorB;
                float  _CheckScale;
                float  _RingCount;
            CBUFFER_END

            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS   : NORMAL;
                float2 uv         : TEXCOORD0;
            };


            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float3 normalWS    : TEXCOORD0;   
                float2 uv          : TEXCOORD1;  
                float3 positionWS  : TEXCOORD2;   
            };

    
            Varyings vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs pos = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionHCS = pos.positionCS;
                output.positionWS  = pos.positionWS;
                output.normalWS    = TransformObjectToWorldNormal(input.normalOS);
                output.uv          = TRANSFORM_TEX(input.uv, _MainTex);
                return output;
            }

       
            half3 Lambert(float3 normalWS, float3 lightDir, half3 lightColor, half3 ambient)
            {
                float NdotL = saturate(dot(normalize(normalWS), normalize(lightDir)));
                return lightColor * NdotL + ambient;
            }

            half3 Gradient(float2 uv, half3 colA, half3 colB)
            {
                return lerp(colA, colB, uv.y);
            }

            half3 Checker(float2 uv, float scale)
            {
                float2 cell  = floor(uv * scale);
                float  check = fmod(cell.x + cell.y, 2.0);
                return half3(check, check, check);
            }

            half3 Rings(float2 uv, float count)
            {
                float dist = length(uv - 0.5) * 2.0;           // 0=centro, 1=borde
                float ring = sin(dist * count * 3.14159) * 0.5 + 0.5;
                return half3(ring, ring * 0.5, 1.0 - ring);
            }

            half4 frag(Varyings input) : SV_Target
            {
                float3 N = normalize(input.normalWS);

                int mode = (int)_FragMode;
                half3 color;

                if (mode == 0)
                {
                    half3 lighting = Lambert(N, _LightDir.xyz, _LightColor.rgb, _Ambient.rgb);
                    color = lighting;
                }
                else if (mode == 1)
                {
                    half4 tex      = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv);
                    half3 lighting = Lambert(N, _LightDir.xyz, _LightColor.rgb, _Ambient.rgb);
                    color = tex.rgb * _TintColor.rgb * lighting;
                }
                else if (mode == 2)
                {
                    color = Gradient(input.uv, _GradColorA.rgb, _GradColorB.rgb);
                }
                else if (mode == 3)
                {
                    color = Checker(input.uv, _CheckScale);
                }
                else
                {
                    color = Rings(input.uv, _RingCount);
                }

                return half4(color, 1.0);
            }

            ENDHLSL
        }
    }
    FallBack "Universal Render Pipeline/Unlit"
}
