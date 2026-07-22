# Windows terminal troubleshooting

Dooma uses Rich to render tables, colors, and Unicode status symbols. A modern
terminal with a Unicode-capable font gives the best results. We recommend
[Windows Terminal](https://github.com/microsoft/terminal) with **Cascadia Mono**
or **Cascadia Code**.

## Missing icons or broken characters

If status icons appear as empty boxes, question marks, or garbled text:

1. Open Windows Terminal **Settings**.
2. Select the profile where you run Dooma, then open **Appearance**.
3. Set **Font face** to `Cascadia Mono`, `Cascadia Code`, or another font that
   includes Unicode symbols.
4. Open a new terminal tab and run `dooma` again.

If the characters are still garbled, confirm that Python is writing UTF-8:

```powershell
python -c "import sys; print(sys.stdout.encoding)"
```

The result should normally be `utf-8`. For the current PowerShell session, you
can enable Python's UTF-8 mode before starting Dooma:

```powershell
$env:PYTHONUTF8 = "1"
dooma
```

In the legacy Command Prompt, `chcp 65001` changes the active code page to
UTF-8. It does not add missing glyphs, so also check the configured font or move
to Windows Terminal.

## Tables wrap or look cramped

Dooma adapts its Rich tables to the available terminal width. If headings or
rows wrap excessively:

- Widen or maximize the terminal window.
- Press <kbd>Ctrl</kbd>+<kbd>-</kbd> in Windows Terminal to reduce the font size.
- Press <kbd>Ctrl</kbd>+<kbd>0</kbd> to restore the default zoom level.

You can inspect the width and height Python detects with:

```powershell
python -c "import shutil; print(shutil.get_terminal_size())"
```

Run the command in the same tab and profile where the layout problem occurs.

## Still having trouble?

When opening an issue, include:

- the terminal application and version;
- the Windows Terminal profile and font;
- the output of `python --version`;
- the encoding and terminal-size command outputs above; and
- a screenshot with any private information removed.

These details help distinguish a font-coverage problem from an encoding or
terminal-width problem.
