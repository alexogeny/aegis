# Aegis Linux Branding Images

Replace these placeholder images with proper branded images before release.

## Required Images

| File | Dimensions | Description |
|------|------------|-------------|
| `banner.png` | 600x100 | Top banner in installer |
| `icon.png` | 64x64 | Application icon |
| `logo.png` | 256x256 | Product logo |
| `wallpaper.png` | 1920x1080 | Background wallpaper |
| `welcome.png` | 800x300 | Welcome screen image |

## Color Scheme (Catppuccin Mocha)

- Background: #1e1e2e
- Surface: #313244
- Text: #cdd6f4
- Accent (Mauve): #cba6f7
- Accent (Pink): #f5c2e7

## Generating Placeholders

To generate placeholder images with ImageMagick:

```bash
cd images/
convert -size 600x100 xc:'#1e1e2e' -fill '#cba6f7' -gravity center -pointsize 36 -annotate 0 'AEGIS LINUX' banner.png
convert -size 64x64 xc:'#cba6f7' -fill '#1e1e2e' -gravity center -pointsize 32 -annotate 0 'A' icon.png
convert -size 256x256 xc:'#1e1e2e' -fill '#cba6f7' -gravity center -pointsize 72 -annotate 0 'AEGIS' logo.png
convert -size 1920x1080 xc:'#1e1e2e' wallpaper.png
convert -size 800x300 xc:'#1e1e2e' -fill '#cdd6f4' -gravity center -pointsize 48 -annotate 0 'Welcome to Aegis Linux' welcome.png
```
