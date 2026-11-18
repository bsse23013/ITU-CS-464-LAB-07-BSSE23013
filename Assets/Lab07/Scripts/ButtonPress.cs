using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

// Feedback on every button: it shrinks a little while pressed (and buzzes on a phone).
public class ButtonPress : MonoBehaviour, IPointerDownHandler, IPointerUpHandler, IPointerExitHandler
{
    public void OnPointerDown(PointerEventData eventData)
    {
        Selectable s = GetComponent<Selectable>();
        if (s != null && !s.interactable) return;
        transform.localScale = Vector3.one * 0.94f;
#if UNITY_ANDROID || UNITY_IOS
        if (SettingsMenu.vibrate) Handheld.Vibrate();
#endif
    }

    public void OnPointerUp(PointerEventData eventData)
    {
        transform.localScale = Vector3.one;
    }

    public void OnPointerExit(PointerEventData eventData)
    {
        transform.localScale = Vector3.one;
    }
}
