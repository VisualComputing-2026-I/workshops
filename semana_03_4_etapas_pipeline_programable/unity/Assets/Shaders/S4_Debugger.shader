Shader "Taller/S4_Debugger"
{
    Properties
    {
        [KeywordEnum(NORMALS_WS, UV, POSITION_WS, DEPTH, VERTEX_ID)]
        _DebugMode ("Modo Debug", Float) = 0

        _DepthRange ("Profundidad máxima visible", Range(1, 50)) = 15.0
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }

        Pass
        {
            Name "S4_Debug"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 4.5
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float _DebugMode;
                float _DepthRange;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS   : NORMAL;
                float2 uv         : TEXCOORD0;
                uint   vertexID   : SV_VertexID;
            };

            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float3 normalWS    : TEXCOORD0;
                float2 uv          : TEXCOORD1;
                float3 positionWS  : TEXCOORD2;
                float  vertexID    : TEXCOORD3;
            };

            Varyings vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs pos = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionHCS = pos.positionCS;
                output.positionWS  = pos.positionWS;
                output.normalWS    = TransformObjectToWorldNormal(input.normalOS);
                output.uv          = input.uv;
                output.vertexID    = (float)input.vertexID / 512.0;
                return output;
            }

            half3 IDToColor(float id)
            {
                return half3(
                    frac(sin(id * 127.1) * 43758.5),
                    frac(sin(id * 311.7) * 43758.5),
                    frac(sin(id * 74.93) * 43758.5)
                );
            }

            half4 frag(Varyings input) : SV_Target
            {
                int mode = (int)_DebugMode;

                if (mode == 0)
                {
                    half3 col = normalize(input.normalWS) * 0.5 + 0.5;
                    return half4(col, 1.0);
                }
            
                else if (mode == 1)
                {
                    return half4(input.uv.x, input.uv.y, 0.0, 1.0);
                }
               
                else if (mode == 2)
                {
                    half3 col = saturate(input.positionWS * 0.1 + 0.5);
                    return half4(col, 1.0);
                }
           
                else if (mode == 3)
                {
                    float dist = length(_WorldSpaceCameraPos - input.positionWS);
                    float d    = 1.0 - saturate(dist / _DepthRange);
                    return half4(d, d, d, 1.0);
                }
         
                else
                {
                    return half4(IDToColor(input.vertexID), 1.0);
                }
            }

            ENDHLSL
        }
    }
    FallBack "Universal Render Pipeline/Unlit"
}
