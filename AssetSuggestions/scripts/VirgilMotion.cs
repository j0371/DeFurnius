using System.Collections;
using UnityEngine;

namespace Virgil.Suggestions
{
    /// <summary>
    /// Code-driven motion for the suggested assets, as a no-risk alternative to the .anim clips.
    /// Add it to the object you want to move. It works on local values, so put the visual under a
    /// parent that you place in the scene. Not tested in the Unity editor.
    /// </summary>
    public class VirgilMotion : MonoBehaviour
    {
        public enum Mode { Bob, Spin, Pulse, Sway }

        [Tooltip("Bob: height in metres. Pulse: scale added at peak. Sway: degrees. Ignored by Spin.")]
        public float amplitude = 0.18f;

        [Tooltip("Seconds per cycle. For Spin, seconds per full turn.")]
        public float period = 4f;

        public Mode mode = Mode.Bob;
        public Vector3 axis = Vector3.up;

        Vector3 m_StartPos;
        Quaternion m_StartRot;
        Vector3 m_StartScale;
        float m_Offset;

        void Awake()
        {
            m_StartPos = transform.localPosition;
            m_StartRot = transform.localRotation;
            m_StartScale = transform.localScale;
            m_Offset = Random.value * period; // so a row of platforms doesn't move in lockstep
        }

        void Update()
        {
            float t = (Time.time + m_Offset) / Mathf.Max(period, 0.01f);
            float s = Mathf.Sin(t * Mathf.PI * 2f);

            switch (mode)
            {
                case Mode.Bob:
                    transform.localPosition = m_StartPos + Vector3.up * (amplitude * s);
                    break;
                case Mode.Spin:
                    transform.localRotation = m_StartRot * Quaternion.AngleAxis(t * 360f, axis);
                    break;
                case Mode.Pulse:
                    transform.localScale = m_StartScale * (1f + amplitude * 0.5f * (1f + s));
                    break;
                case Mode.Sway:
                    transform.localRotation = m_StartRot * Quaternion.AngleAxis(amplitude * s, axis);
                    break;
            }
        }

        /// <summary>Slides the object down by distance over seconds with smoothstep easing, then optionally disables it.</summary>
        public void Lower(float distance, float seconds, bool disableAtEnd = false)
        {
            StopAllCoroutines();
            StartCoroutine(LowerRoutine(distance, seconds, disableAtEnd));
        }

        IEnumerator LowerRoutine(float distance, float seconds, bool disableAtEnd)
        {
            enabled = false; // stop Bob/Sway from fighting the slide
            Vector3 from = transform.localPosition;
            Vector3 to = from + Vector3.down * distance;
            for (float e = 0f; e < seconds; e += Time.deltaTime)
            {
                float k = Mathf.Clamp01(e / seconds);
                transform.localPosition = Vector3.Lerp(from, to, k * k * (3f - 2f * k));
                yield return null;
            }
            transform.localPosition = to;
            if (disableAtEnd) gameObject.SetActive(false);
        }
    }
}
