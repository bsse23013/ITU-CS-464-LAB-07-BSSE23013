using TMPro;
using UnityEngine;
using UnityEngine.UI;

// Loadout screen: tapping a skin changes the big preview and moves the orange frame.
public class SkinPicker : MonoBehaviour
{
    public Image preview;
    public TMP_Text skinName;
    public RectTransform marker;
    public RectTransform[] tiles;
    public Color[] colors;
    public string[] names;

    void Start()
    {
        Pick(0);
    }

    public void Pick(int i)
    {
        preview.color = colors[i];
        skinName.text = names[i];
        marker.localPosition = tiles[i].localPosition;
    }
}
