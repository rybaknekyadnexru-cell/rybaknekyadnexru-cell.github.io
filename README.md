# Nik Rybak Games

Static site on GitHub Pages: https://rybaknekyadnexru-cell.github.io/

- `games.json` - every game and the ad networks it uses.
- `build.py` - generates `index.html` and `<game>/privacy/index.html` (English and Russian).
- `assets/site.css` - one stylesheet, light and dark.
- `app-ads.txt` - AdMob publisher line (added once the AdMob account exists).

## Add a game

1. Add an entry to `games.json` (`key`, `name`, taglines, `effective`, `stores`, `ads`, `purchases`).
2. Run `python build.py` (fails on curly quotes, dashes and the ellipsis character).
3. Commit and push. The policy URL is `https://rybaknekyadnexru-cell.github.io/<key>/privacy/`.
