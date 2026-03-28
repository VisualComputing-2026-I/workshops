using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace ProceduralModeling
{
    public class ProceduralCameraController : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float moveSpeed = 6f;
        [SerializeField] private float sprintMultiplier = 2.2f;
        [SerializeField] private float verticalSpeed = 4f;

        [Header("Rotation")]
        [SerializeField] private bool requireRightMouseForLook = true;
        [SerializeField] private float mouseSensitivity = 120f;
        [SerializeField] private float maxPitch = 85f;

        private float yaw;
        private float pitch;

        private void Awake()
        {
            Vector3 currentEuler = transform.rotation.eulerAngles;
            yaw = currentEuler.y;
            pitch = NormalizeAngle(currentEuler.x);
        }

        private void Update()
        {
            float deltaTime = Time.deltaTime;
            UpdateRotation(deltaTime);
            UpdateMovement(deltaTime);
        }

        private void UpdateMovement(float deltaTime)
        {
            Vector3 inputDirection = GetMovementInput();
            if (inputDirection.sqrMagnitude > 1f)
            {
                inputDirection.Normalize();
            }

            float speed = moveSpeed;
            if (IsSprintPressed())
            {
                speed *= sprintMultiplier;
            }

            Vector3 horizontalMovement = (transform.forward * inputDirection.z + transform.right * inputDirection.x) * (speed * deltaTime);
            Vector3 verticalMovement = Vector3.up * (inputDirection.y * verticalSpeed * deltaTime);
            transform.position += horizontalMovement + verticalMovement;
        }

        private void UpdateRotation(float deltaTime)
        {
            if (requireRightMouseForLook && !IsLookActive())
            {
                return;
            }

            Vector2 lookInput = GetLookInput();
            yaw += lookInput.x * mouseSensitivity * deltaTime;
            pitch -= lookInput.y * mouseSensitivity * deltaTime;
            pitch = Mathf.Clamp(pitch, -maxPitch, maxPitch);

            transform.rotation = Quaternion.Euler(pitch, yaw, 0f);
        }

        private Vector3 GetMovementInput()
        {
            float horizontal = 0f;
            float forward = 0f;
            float vertical = 0f;

#if ENABLE_INPUT_SYSTEM
            Keyboard keyboard = Keyboard.current;
            if (keyboard != null)
            {
                if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed)
                {
                    horizontal -= 1f;
                }

                if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed)
                {
                    horizontal += 1f;
                }

                if (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed)
                {
                    forward += 1f;
                }

                if (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed)
                {
                    forward -= 1f;
                }

                if (keyboard.eKey.isPressed || keyboard.pageUpKey.isPressed)
                {
                    vertical += 1f;
                }

                if (keyboard.qKey.isPressed || keyboard.pageDownKey.isPressed)
                {
                    vertical -= 1f;
                }
            }
#else
            horizontal = Input.GetAxisRaw("Horizontal");
            forward = Input.GetAxisRaw("Vertical");
            if (Input.GetKey(KeyCode.E) || Input.GetKey(KeyCode.PageUp))
            {
                vertical += 1f;
            }

            if (Input.GetKey(KeyCode.Q) || Input.GetKey(KeyCode.PageDown))
            {
                vertical -= 1f;
            }
#endif

            return new Vector3(horizontal, vertical, forward);
        }

        private Vector2 GetLookInput()
        {
#if ENABLE_INPUT_SYSTEM
            Mouse mouse = Mouse.current;
            if (mouse == null)
            {
                return Vector2.zero;
            }

            return mouse.delta.ReadValue();
#else
            return new Vector2(Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y"));
#endif
        }

        private bool IsSprintPressed()
        {
#if ENABLE_INPUT_SYSTEM
            Keyboard keyboard = Keyboard.current;
            return keyboard != null && (keyboard.leftShiftKey.isPressed || keyboard.rightShiftKey.isPressed);
#else
            return Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
#endif
        }

        private bool IsLookActive()
        {
#if ENABLE_INPUT_SYSTEM
            Mouse mouse = Mouse.current;
            return mouse != null && mouse.rightButton.isPressed;
#else
            return Input.GetMouseButton(1);
#endif
        }

        private static float NormalizeAngle(float angle)
        {
            if (angle > 180f)
            {
                angle -= 360f;
            }

            return angle;
        }
    }
}
