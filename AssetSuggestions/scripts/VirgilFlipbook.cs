using UnityEngine;

namespace Virgil.Suggestions
{
    /// <summary>
    /// Plays a sprite sheet (for example flame_sheet_4x4.png) on a quad by stepping the material's
    /// texture offset. Put it on a Quad or any object whose material is Unlit/Transparent Cutout or
    /// similar with a texture. Set the texture to Point filter, Wrap Mode Clamp. Not tested in the editor.
    /// </summary>
    [RequireComponent(typeof(Renderer))]
    public class VirgilFlipbook : MonoBehaviour
    {
        public int columns = 4;
        public int rows = 4;
        public float framesPerSecond = 16f;
        public bool loop = true;

        Material m_Material;
        float m_Time;

        void Awake()
        {
            m_Material = GetComponent<Renderer>().material; // instance, so each flipbook has its own offset
            m_Material.mainTextureScale = new Vector2(1f / columns, 1f / rows);
        }

        void OnEnable()
        {
            m_Time = 0f;
        }

        void Update()
        {
            m_Time += Time.deltaTime;
            int total = columns * rows;
            int frame = (int)(m_Time * framesPerSecond);
            if (!loop && frame >= total)
            {
                enabled = false;
                return;
            }

            frame %= total;
            int col = frame % columns;
            int row = frame / columns;
            // Texture space has v=0 at the bottom, sheets are read from the top-left.
            m_Material.mainTextureOffset = new Vector2(col / (float)columns, 1f - (row + 1) / (float)rows);
        }

        void OnDestroy()
        {
            if (m_Material != null) Destroy(m_Material);
        }
    }
}
