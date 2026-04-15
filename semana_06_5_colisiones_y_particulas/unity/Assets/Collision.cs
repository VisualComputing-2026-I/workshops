using UnityEngine;

public class ColisionParticulas : MonoBehaviour
{
    public ParticleSystem efectoPrefab;

    private void OnCollisionEnter(Collision collision)
    {
        if (efectoPrefab != null && collision.contactCount > 0)
        {
            Vector3 punto = collision.contacts[0].point;
            Quaternion rot = Quaternion.LookRotation(collision.contacts[0].normal);

            ParticleSystem fx = Instantiate(efectoPrefab, punto, rot);
            fx.Play();

            Destroy(fx.gameObject, 2f);
        }
    }
}