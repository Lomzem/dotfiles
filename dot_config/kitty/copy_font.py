from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
FONT_FILE = SCRIPT_DIR / "font.conf"

fontdata = None

with open(FONT_FILE, "r") as f:
    lines = f.readlines()
    for line in lines:
        if "style" in line:
            fontdata = "family" + line.split("family")[-1]

if fontdata:
    with open(FONT_FILE, "w") as f:
        _ = f.writelines(
            [
                "# vim:fileencoding=utf-8:foldmethod=marker\n",
                "# BEGIN_KITTY_FONTS\n",
                f"font_family       {fontdata}",
                f"bold_font         {fontdata}",
                f"italic_font       {fontdata}",
                f"bold_italic_font  {fontdata}",
                "# END_KITTY_FONTS",
            ]
        )
