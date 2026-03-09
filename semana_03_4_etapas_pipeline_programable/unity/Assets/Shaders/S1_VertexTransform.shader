Shader "Taller/S1_VertexTransform"
{
    Properties
    {
        _WaveAmplitude ("Wave Amplitude",  Range(0, 0.5)) = 0.15
        _WaveFrequency ("Wave Frequency",  Range(0, 10))  = 3.0
        _WaveSpeed     ("Wave Speed",      Range(0, 5))   = 1.5

        [KeywordEnum(CLIP, WORLD, VIEW)]
        _ShowSpace ("Mostrar espacio", Float) = 0
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }

        Pass
        {
            Name "S1_Forward"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 4.5
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float _WaveAmplitude;
                float _WaveFrequency;
                float _WaveSpeed;
                float _ShowSpace;
            CBUFFER_END


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
                float3 positionVS  : TEXCOORD3;   
                float3 waveColor   : TEXCOORD4;  
            };

  
            Varyings vert(Attributes input)
            {
                Varyings output;

    
                float4 positionWS4 = mul(UNITY_MATRIX_M, input.positionOS);
                float3 posWS = positionWS4.xyz;

         
                float wave = sin(posWS.x * _WaveFrequency + _Time.y * _WaveSpeed)
                           * cos(posWS.z * _WaveFrequency + _Time.y * _WaveSpeed);
                posWS.y += wave * _WaveAmplitude;

                float4 positionVS4 = mul(UNITY_MATRIX_V, float4(posWS, 1.0));
                float3 posVS = positionVS4.xyz;


                output.positionHCS = mul(UNITY_MATRIX_P, positionVS4);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.uv          = input.uv;
                output.positionWS  = posWS;
                output.positionVS  = posVS;
                output.waveColor = float3(wave * 0.5 + 0.5,
                                          0.2,
                                          1.0 - (wave * 0.5 + 0.5));

                return output;
            }


            half4 frag(Varyings input) : SV_Target
            {
                int mode = (int)_ShowSpace;

                if (mode == 0)
                    return half4(input.waveColor, 1.0);

                else if (mode == 1)
                    return half4(normalize(input.normalWS) * 0.5 + 0.5, 1.0);

                else
                    return half4(input.uv.x, input.uv.y, 0.0, 1.0);
            }

            ENDHLSL
        }
    }
    FallBack "Universal Render Pipeline/Unlit"
}
