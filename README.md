# Nik Rybak Games

Static site on GitHub Pages: https://rybaknekyadnexru-cell.github.io/

- `games.json` - every game and the ad networks it uses.
- `build.py` - generates every page: English at `/` and `/<game>/privacy/`, other languages at `/<lang>/...`. Shared header: language select and theme switch (dark by default, choice remembered).
- `assets/site.css` - one stylesheet, dark and light themes. `assets/games/<key>.png` - game icons (216x216).
- `publish.ps1` - build, commit and push in one step: `.\publish.ps1 "what changed"`.
- `app-ads.txt` - AdMob publisher line (added once the AdMob account exists).

## Add a game

1. Add an entry to `games.json` (`key`, `name`, `tagline` per language, `effective`, `stores`, `ads`, `purchases`) and its icon as `assets/games/<key>.png`.
2. Run `.\publish.ps1 "feat: add <game>"` (the build fails on curly quotes, dashes and the ellipsis character).
3. The policy URL is `https://rybaknekyadnexru-cell.github.io/<key>/privacy/`.

## Add a language

Add a block to `TEXT` in `build.py` with the same keys; every page and the header select get it.

## Preview locally

`python -m http.server 8090` in this folder, then open http://localhost:8090/.

## License

All rights reserved, see [LICENSE](LICENSE).
