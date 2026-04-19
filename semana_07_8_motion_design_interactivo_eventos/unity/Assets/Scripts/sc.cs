using UnityEngine;
using System.Collections;

public class sc : MonoBehaviour
{
    public Animator animator;

    // Update is called once per frame
    void Update()
    {
        if(Input.GetKeyDown(KeyCode.Space))
        {
            animator.SetTrigger("jump");
        }

        if(Input.GetKeyDown(KeyCode.W))
        {
            animator.SetBool("isRunning", true);
        }

        if(Input.GetKeyUp(KeyCode.W))
        {
            animator.SetBool("isRunning", false);
        }

        if(Input.GetKeyDown(KeyCode.D))
        {
            animator.SetBool("isDancing", !animator.GetBool("isDancing"));
        }
    }
}
