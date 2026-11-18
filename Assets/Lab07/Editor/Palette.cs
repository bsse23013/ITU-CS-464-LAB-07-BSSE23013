using TMPro;
using UnityEngine;

// Colours (60-30-10) and the art / fonts, used only by the scene builder.
public static class Palette
{
    public static readonly Color BgDeep   = Hex("0F1230");
    public static readonly Color BgMid    = Hex("1A1F52");
    public static readonly Color Panel    = Hex("252B6B");
    public static readonly Color PanelHi  = Hex("343C94");
    public static readonly Color Stroke   = Hex("7078E0");
    public static readonly Color Text     = Hex("F6F4FF");
    public static readonly Color Muted    = Hex("B9BEF0");
    public static readonly Color Accent   = Hex("FF8A1F");
    public static readonly Color Green    = Hex("8EE67E");
    public static readonly Color Gold     = Hex("FFE680");
    public static readonly Color Red      = Hex("F04458");
    public static readonly Color Disabled = Hex("1E2250");

    public static Color Hex(string hex)
    {
        Color c;
        ColorUtility.TryParseHtmlString("#" + hex, out c);
        return c;
    }
}

public static class Art
{
    public static TMP_FontAsset Display { get { return Resources.Load<TMP_FontAsset>("Lab07/Fonts/LilitaOne-Regular SDF"); } }
    public static TMP_FontAsset Body    { get { return Resources.Load<TMP_FontAsset>("Lab07/Fonts/Poppins-Regular SDF"); } }
    public static TMP_FontAsset Bold    { get { return Resources.Load<TMP_FontAsset>("Lab07/Fonts/Poppins-SemiBold SDF"); } }

    public static Sprite Sprite(string name)
    {
        return Resources.Load<Sprite>("Lab07/Sprites/" + name);
    }
}
