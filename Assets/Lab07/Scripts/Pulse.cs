using UnityEngine;

// Makes the "TAP TO START" text grow and shrink slowly.
public class Pulse : MonoBehaviour
{
    void Update()
    {
        transform.localScale = Vector3.one * (1f + 0.06f * Mathf.Sin(Time.unscaledTime * 3f));
    }
}
