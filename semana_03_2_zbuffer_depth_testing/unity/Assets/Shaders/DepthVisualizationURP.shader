Shader "Custom/DepthVisualizationURP"
{
    // =========================================================================
    // Shader compatible con URP (Universal Render Pipeline) que visualiza
    // el depth buffer en escala de grises.
    // Incluye modo lineal y no-lineal.
    // =========================================================================
    Properties
    {
        [Toggle(_LINEARMODE)] _LinearMode ("Modo Lineal", Float) = 0
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Opaque"
            "RenderPipeline" = "UniversalPipeline"
            "Queue" = "Geometry"
        }
        LOD 100

        Pass
        {
            Name "DepthVis"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma shader_feature_local _LINEARMODE

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float  rawDepth   : TEXCOORD0;
                float  linearZ    : TEXCOORD1;
            };

            Varyings vert(Attributes input)
            {
                Varyings o;
                VertexPositionInputs vpi = GetVertexPositionInputs(input.positionOS.xyz);
                o.positionCS = vpi.positionCS;

                // Profundidad clip-space normalizada
                o.rawDepth = o.positionCS.z / o.positionCS.w;
                #if !defined(UNITY_REVERSED_Z)
                    o.rawDepth = o.rawDepth * 0.5 + 0.5;
                #endif

                // Distancia lineal desde la camara
                o.linearZ = -TransformWorldToView(vpi.positionWS).z;

                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                float d;

                #ifdef _LINEARMODE
                    d = (i.linearZ - _ProjectionParams.y) /
                        (_ProjectionParams.z - _ProjectionParams.y);
                    d = saturate(d);
                #else
                    d = i.rawDepth;
                    #if defined(UNITY_REVERSED_Z)
                        d = 1.0 - d;
                    #endif
                #endif

                return half4(d, d, d, 1.0);
            }
            ENDHLSL
        }
    }

    FallBack "Universal Render Pipeline/Lit"
}
