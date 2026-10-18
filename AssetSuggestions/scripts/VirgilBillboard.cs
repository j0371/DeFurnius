using UnityEngine;

namespace Virgil.Suggestions
{
    /// <summary>
    /// Turns the object to face the main camera. Use for tertiary sprites (embers, flames, snow).
    /// Not tested in the editor.
    /// </summary>
    public class VirgilBillboard : MonoBehaviour
    {
        [Tooltip("Only rotate around Y, so tall sprites stay upright.")]
        public bool yAxisOnly = true;

        Transform m_Camera;

        void LateUpdate()
        {
            if (m_Camera == null)
            {
                Camera main = Camera.main;
                if (main == null) return;
                m_Camera = main.transform;
            }

            Vector3 toCamera = transform.position - m_Camera.position;
            if (yAxisOnly) toCamera.y = 0f;
            if (toCamera.sqrMagnitude < 1e-6f) return;
            transform.rotation = Quaternion.LookRotation(toCamera, Vector3.up);
        }
    }
}
