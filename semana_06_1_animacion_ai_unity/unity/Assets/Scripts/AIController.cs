using UnityEngine;
using UnityEngine.AI;

public enum AIState { Idle, Patrol, Chase }

public class AIController : MonoBehaviour
{
    [Header("Waypoints")]
    public Transform[] waypoints;

    [Header("Detection")]
    public Transform player;
    public float detectionRadius = 10f;
    public float loseRadius = 15f;

    [Header("Speeds")]
    public float patrolSpeed = 2f;
    public float chaseSpeed = 5f;

    private NavMeshAgent agent;
    private Animator animator;
    private AIState currentState = AIState.Idle;
    private int currentWaypointIndex = 0;
    private float idleTimer = 0f;

    void Start()
    {
        agent = GetComponent<NavMeshAgent>();
        animator = GetComponent<Animator>();
        agent.stoppingDistance = 0.5f;
        agent.isStopped = true;
        Debug.Log("Inicio en IDLE");
        SetWaypoint(0); 
    }

    void Update()
    {
        switch (currentState)
        {
            case AIState.Idle:   HandleIdle();   break;
            case AIState.Patrol: HandlePatrol(); break;
            case AIState.Chase:  HandleChase();  break;
        }

        animator.SetFloat("Speed", agent.velocity.magnitude);
    }

    void HandleIdle()
    {
        agent.isStopped = true;
        idleTimer += Time.deltaTime;
        if (idleTimer >= 2f)
        {
            idleTimer = 0f;
            agent.isStopped = false;
            currentState = AIState.Patrol;
            SetWaypoint(0); 
            Debug.Log("IDLE → PATROL, yendo a WP_0");
        }
    }

    private bool waitingForPath = false;

    void HandlePatrol()
    {
        if (currentWaypointIndex >= 2)
            agent.speed = 5f;   
        else
            agent.speed = 2f;


        if (waitingForPath)
        {
            if (agent.pathPending) return; 
            waitingForPath = false;
        }

        if (agent.hasPath && agent.remainingDistance <= 0.5f)
        {
            currentWaypointIndex = (currentWaypointIndex + 1) % waypoints.Length;
            SetWaypoint(currentWaypointIndex);
            waitingForPath = true; 
        }

        if (PlayerDetected())
        {
            currentState = AIState.Chase;
        }
    }

    void HandleChase()
    {
        agent.speed = chaseSpeed;
        agent.SetDestination(player.position);

        if (PlayerLost())
        {
            currentState = AIState.Patrol;
            SetWaypoint(currentWaypointIndex);
        }
    }

    void SetWaypoint(int index)
    {
        currentWaypointIndex = index;
        agent.speed = (index >= 2) ? 5f : 2f;
        agent.SetDestination(waypoints[index].position);
    }

    bool PlayerDetected() =>
        Vector3.Distance(transform.position, player.position) < detectionRadius;

    bool PlayerLost() =>
        Vector3.Distance(transform.position, player.position) > loseRadius;

    void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, detectionRadius);
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, loseRadius);
    }
}