Shader "Taller/S3_Wireframe"
{
    Properties
    {
        [KeywordEnum(WIREFRAME, NORMALS, SOLID_WIRE)]
        _Mode ("Modo", Float) = 0

        _WireColor     ("Color del Wire",    Color)              = (0, 1, 0.4, 1)
        _FaceColor     ("Color de la cara",  Color)              = (0.05, 0.05, 0.15, 1)
        _WireThickness ("Grosor del Wire",   Range(0.001, 0.08)) = 0.02
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }

        Pass
        {
            Name "S3_Wireframe"
            Tags { "LightMode"="UniversalForward" }
            Cull Off 

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 4.5
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float  _Mode;
                float4 _WireColor;
                float4 _FaceColor;
                float  _WireThickness;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS   : NORMAL;
                float2 uv         : TEXCOORD0;
                float2 baryXY     : TEXCOORD1;
            };

            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float3 normalWS    : TEXCOORD0;
                float3 bary        : TEXCOORD1;
            };

            Varyings vert(Attributes input)
            {
                Varyings output;
                output.positionHCS = TransformObjectToHClip(input.positionOS.xyz);
                output.normalWS    = TransformObjectToWorldNormal(input.normalOS);
                float z   = 1.0 - input.baryXY.x - input.baryXY.y;
                output.bary = float3(input.baryXY.x, input.baryXY.y, z);
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                int mode = (int)_Mode;

                if (mode == 0)
                {
                    float3 b    = input.bary;
                    float  edge = min(min(b.x, b.y), b.z);
                    float  wire = 1.0 - smoothstep(0.0, _WireThickness, edge);
                    half3  col  = lerp(_FaceColor.rgb, _WireColor.rgb, wire);
                    return half4(col, 1.0);
                }
       
                else if (mode == 1)
                {
                    half3 col = normalize(input.normalWS) * 0.5 + 0.5;
                    return half4(col, 1.0);
                }
                else
                {
                    float3 b    = input.bary;
                    float  edge = min(min(b.x, b.y), b.z);
                    float  wire = 1.0 - smoothstep(0.0, _WireThickness * 0.5, edge);
                    half3  faceCol = normalize(input.normalWS) * 0.5 + 0.5;
                    half3  col     = lerp(faceCol, _WireColor.rgb, wire);
                    return half4(col, 1.0);
                }
            }

            ENDHLSL
        }
    }
    FallBack "Universal Render Pipeline/Unlit"
}
