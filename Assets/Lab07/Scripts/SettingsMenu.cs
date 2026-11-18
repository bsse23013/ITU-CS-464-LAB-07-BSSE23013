using TMPro;
using UnityEngine;
using UnityEngine.UI;

// Settings screen: two switches and a slider.
public class SettingsMenu : MonoBehaviour
{
    public static bool vibrate = true;

    public Image dimmer;              // a black layer over the whole UI
    public TMP_Text brightnessLabel;
    public GameObject tipsText;       // the tip on the Main Menu

    public void SetVibrate(bool on)
    {
        vibrate = on;
    }

    public void SetTips(bool on)
    {
        tipsText.SetActive(on);
    }

    public void SetBrightness(float value)
    {
        dimmer.color = new Color(0f, 0f, 0f, (1f - value) * 0.8f);
        brightnessLabel.text = Mathf.RoundToInt(value * 100f) + "%";
    }
}
