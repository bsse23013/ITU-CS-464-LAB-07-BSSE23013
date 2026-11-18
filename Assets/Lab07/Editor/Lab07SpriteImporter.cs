using UnityEditor;
using UnityEngine;

// Every PNG in Assets/Lab07/Resources/Lab07/Sprites is a UI sprite. This sets the import
// options automatically so nothing has to be clicked by hand (and a fresh clone just works):
//   - Sprite (2D and UI), uncompressed, no mipmaps, full rect (no tight mesh)
//   - nine-slice borders from the file name:  rrect_b44.png -> 44 px border on all sides
//   - grid_t.png repeats (it is tiled across the arena)
public class Lab07SpriteImporter : AssetPostprocessor
{
    const string Folder = "Assets/Lab07/Resources/Lab07/Sprites/";

    void OnPreprocessTexture()
    {
        if (!assetPath.StartsWith(Folder)) return;

        TextureImporter ti = (TextureImporter)assetImporter;
        ti.textureType = TextureImporterType.Sprite;
        ti.spriteImportMode = SpriteImportMode.Single;
        ti.spritePixelsPerUnit = 100f;
        ti.mipmapEnabled = false;
        ti.alphaIsTransparency = true;
        ti.textureCompression = TextureImporterCompression.Uncompressed;
        ti.filterMode = FilterMode.Bilinear;
        ti.wrapMode = assetPath.EndsWith("grid_t.png") ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;

        TextureImporterSettings s = new TextureImporterSettings();
        ti.ReadTextureSettings(s);
        s.spriteMeshType = SpriteMeshType.FullRect;
        s.spriteExtrude = 0;

        string name = System.IO.Path.GetFileNameWithoutExtension(assetPath);
        int at = name.LastIndexOf("_b");
        int border = 0;
        if (at > 0) int.TryParse(name.Substring(at + 2), out border);
        s.spriteBorder = new Vector4(border, border, border, border);
        ti.SetTextureSettings(s);
    }
}
