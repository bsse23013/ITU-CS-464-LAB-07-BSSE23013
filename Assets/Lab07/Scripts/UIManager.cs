using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

// Shows one screen at a time. Every button in the scene calls one of these public methods
// (set in the Button's OnClick list in the Inspector).
public class UIManager : MonoBehaviour
{
    // 0 Title, 1 Main Menu, 2 Levels, 3 Loadout, 4 Game, 5 Results, 6 Shop, 7 Settings, 8 Credits
    public GameObject[] panels;
    public GameObject pausePanel;

    // the ease curves: edit them in the Inspector to change how the screens move
    public AnimationCurve slideCurve = AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);
    public AnimationCurve popCurve = new AnimationCurve(new Keyframe(0f, 0f), new Keyframe(0.65f, 1.15f), new Keyframe(1f, 1f));
    public float duration = 0.3f;

    public TMP_Text[] levelLabels;
    public TMP_Text resultTitle;
    public Image resultBanner;
    public GameObject starsRow;
    public GameObject nextButton;
    public Shop shop;

    void Start()
    {
        Show(0);
    }

    public void Show(int index)
    {
        StopAllCoroutines();
        Time.timeScale = 1f;
        pausePanel.SetActive(false);
        for (int i = 0; i < panels.Length; i++) panels[i].SetActive(false);
        panels[index].SetActive(true);
        bool pop = index == 4 || index == 5;     // the game and results pop up, the menus slide in
        StartCoroutine(Animate(panels[index], pop));
    }

    public void SelectLevel(int number)
    {
        foreach (TMP_Text label in levelLabels) label.text = "LEVEL " + number;
        Show(3);
    }

    public void Pause()
    {
        Time.timeScale = 0f;                     // the game stops, the menu animation uses unscaled time
        pausePanel.SetActive(true);
        StartCoroutine(Animate(pausePanel, true));
    }

    public void Resume()
    {
        Time.timeScale = 1f;
        pausePanel.SetActive(false);
    }

    public void Win()
    {
        resultTitle.text = "LEVEL CLEARED!";
        resultBanner.color = new Color(1f, 0.9f, 0.5f);
        starsRow.SetActive(true);
        nextButton.SetActive(true);
        shop.AddCoins(50);
        Show(5);
    }

    public void Lose()
    {
        resultTitle.text = "LEVEL FAILED";
        resultBanner.color = new Color(0.94f, 0.27f, 0.35f);
        starsRow.SetActive(false);
        nextButton.SetActive(false);
        Show(5);
    }

    IEnumerator Animate(GameObject panel, bool pop)
    {
        CanvasGroup group = panel.GetComponent<CanvasGroup>();
        RectTransform rt = panel.GetComponent<RectTransform>();
        for (float t = 0f; t < duration; t += Time.unscaledDeltaTime)
        {
            float k = t / duration;
            if (pop) rt.localScale = Vector3.one * (0.85f + 0.15f * popCurve.Evaluate(k));
            else rt.anchoredPosition = new Vector2(150f * (1f - slideCurve.Evaluate(k)), 0f);
            group.alpha = Mathf.Clamp01(k * 2f);
            yield return null;
        }
        group.alpha = 1f;
        rt.localScale = Vector3.one;
        rt.anchoredPosition = Vector2.zero;
    }
}
