using UnityEngine;
using UnityEngine.InputSystem;

public class EnergyOnClick : MonoBehaviour
{
    private ParticleSystem energyParticles;
    private bool isEmitting = false;

    void Start()
    {
        energyParticles = GetComponentInChildren<ParticleSystem>();
        energyParticles.Stop();
    }

    void Update()
    {
        
        if (Mouse.current.leftButton.wasPressedThisFrame)
        {
            Ray ray = Camera.main.ScreenPointToRay(
                Mouse.current.position.ReadValue()
            );
            RaycastHit hit;

            if (Physics.Raycast(ray, out hit))
            {
                if (hit.collider.gameObject == this.gameObject)
                {
                    ToggleParticles();
                }
            }
        }
    }

    void ToggleParticles()
    {
        if (isEmitting)
        {
            energyParticles.Stop();
            isEmitting = false;
        }
        else
        {
            energyParticles.Play();
            isEmitting = true;
        }
    }
}