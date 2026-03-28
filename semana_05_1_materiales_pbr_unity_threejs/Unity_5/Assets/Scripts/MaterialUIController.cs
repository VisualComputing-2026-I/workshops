using UnityEngine;
using UnityEngine.UI;

public class MaterialUIController : MonoBehaviour
{
    public Material sphereMaterial;
    public Material cubeMaterial;

    public Slider sphereSmoothness;
    public Slider cubeMetallic;
    public Slider cubeSmoothness;

    void Start()
    {
        sphereSmoothness.onValueChanged.AddListener(SetSphereSmoothness);
        cubeMetallic.onValueChanged.AddListener(SetCubeMetallic);
        cubeSmoothness.onValueChanged.AddListener(SetCubeSmoothness);
    }

    void SetSphereSmoothness(float value)
    {
        sphereMaterial.SetFloat("_Smoothness", value);
    }

    void SetCubeMetallic(float value)
    {
        cubeMaterial.SetFloat("_Metallic", value);
    }

    void SetCubeSmoothness(float value)
    {
        cubeMaterial.SetFloat("_Smoothness", value);
    }
}