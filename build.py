"""Builds the static site from games.json: a home page and one privacy page per game, per language.

URLs: English at /, /<game>/privacy/ ; other languages at /<lang>/, /<lang>/<game>/privacy/.
Add a game: append it to games.json, run `python build.py`, then `./publish.ps1 "message"`.
Add a language: add a block to TEXT (same keys) - every page gets it and the header select lists it.
Typography: straight double quotes "" and the plain hyphen-minus only (checked on build).
"""

import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
FORBIDDEN = re.compile("[–—«»“”„‘’…]")
esc = html.escape

TEXT = {
    "en": {
        "label": "English",
        "tagline": "Small offline puzzle games.",
        "games": "Games",
        "policy": "Privacy policy",
        "title": "{name}: privacy policy",
        "effective": "Effective {date}",
        "theme": "Switch theme",
        "language": "Language",
        "summary": "No account, no sign-up and no server of our own. Your progress and settings stay on your device. Only the ad network and the app store receive the data they need to show ads and process purchases.",
        "device_h": "Data on your device",
        "device": "Puzzle progress, statistics, streaks, hints, settings and the items you own. Android may include them in your device backup if backup is on; we never receive this data.",
        "ads_h": "Advertising",
        "ads": "The {store} version shows ads through {network} ({company}). To show and measure ads and to prevent fraud, it may process the advertising ID, IP address and approximate location, device and app information, ad interactions and diagnostics. In the EEA, the UK, Switzerland and some US states the app asks for your consent first, and you can change it later in Settings. You can reset the advertising ID or opt out of personalized ads in your device settings. Details: <a href=\"{privacy}\">{company} privacy policy</a>, <a href=\"{partner}\">how {company} uses data from partner apps</a>.",
        "no_ads": "Other versions show no ads.",
        "buy_h": "Purchases",
        "buy": "Purchases are processed by {stores} under their own terms. We only receive a confirmation of which item you own and never see your payment details.",
        "and": " and ",
        "kids_h": "Children",
        "kids": "{name} is not directed at children, and we do not knowingly collect data from children under 13.",
        "rights_h": "Your choices",
        "rights": "Uninstalling the app deletes its data from your device. We hold no personal data, so there is nothing for us to export or erase. Questions about advertising data go to the ad network, questions about purchases go to the app store.",
        "security_h": "Security",
        "security": "The ad and store SDKs send data encrypted (TLS).",
        "changes_h": "Changes",
        "changes": "When something changes, we update this page and its effective date.",
    },
    "ru": {
        "label": "Русский",
        "tagline": "Небольшие офлайн-головоломки.",
        "games": "Игры",
        "policy": "Политика конфиденциальности",
        "title": "{name}: политика конфиденциальности",
        "effective": "Действует с {date}",
        "theme": "Сменить тему",
        "language": "Язык",
        "summary": "Без аккаунта, регистрации и собственного сервера. Прогресс и настройки хранятся только на вашем устройстве. Данные получают лишь рекламная сеть и магазин приложений - ровно то, что нужно для показа рекламы и покупок.",
        "device_h": "Данные на устройстве",
        "device": "Прогресс, статистика, серии, подсказки, настройки и купленные предметы. Android может включить их в резервную копию устройства, если она включена; мы эти данные не получаем.",
        "ads_h": "Реклама",
        "ads": "Версия для {store} показывает рекламу через {network} ({company}). Для показа и учёта рекламы и защиты от мошенничества могут обрабатываться рекламный идентификатор, IP-адрес и приблизительное местоположение, сведения об устройстве и приложении, взаимодействие с рекламой и диагностика. В ЕЭЗ, Великобритании, Швейцарии и некоторых штатах США приложение сначала спрашивает согласие, изменить его можно в настройках. Рекламный идентификатор можно сбросить, а персонализацию отключить в настройках устройства. Подробнее: <a href=\"{privacy}\">политика конфиденциальности {company}</a>, <a href=\"{partner}\">как {company} использует данные из приложений партнёров</a>.",
        "no_ads": "Другие версии рекламу не показывают.",
        "buy_h": "Покупки",
        "buy": "Покупки обрабатывают {stores} по своим правилам. Мы получаем только подтверждение того, каким предметом вы владеете, и не видим платёжных данных.",
        "and": " и ",
        "kids_h": "Дети",
        "kids": "{name} не предназначена для детей, и мы сознательно не собираем данные детей младше 13 лет.",
        "rights_h": "Ваш выбор",
        "rights": "Удаление приложения удаляет его данные с устройства. Мы не храним персональных данных, поэтому выгружать или удалять у нас нечего. Вопросы о рекламных данных - к рекламной сети, о покупках - к магазину приложений.",
        "security_h": "Безопасность",
        "security": "Рекламный SDK и SDK магазина передают данные в зашифрованном виде (TLS).",
        "changes_h": "Изменения",
        "changes": "При изменениях мы обновляем эту страницу и дату вступления в силу.",
    },
}
DEFAULT = "en"

THEME_JS = "(function(){try{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}catch(e){}})()"
TOGGLE_JS = ("function toggleTheme(){var r=document.documentElement,t=r.dataset.theme==='light'?'dark':'light';"
             "r.dataset.theme=t;try{localStorage.setItem('theme',t)}catch(e){}}")
SUN = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4'
       'M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')


MONTHS_EN = "January February March April May June July August September October November December".split()


def date_text(iso, lang):
    d = datetime.date.fromisoformat(iso)
    return f"{MONTHS_EN[d.month - 1]} {d.day}, {d.year}" if lang == "en" else d.strftime("%d.%m.%Y")


def url(lang, path=""):
    return ("/" if lang == DEFAULT else f"/{lang}/") + path


def page(lang, path, title, body, site):
    t = TEXT[lang]
    options = "".join(f'<option value="{url(code, path)}"{" selected" if code == lang else ""}>{v["label"]}</option>'
                      for code, v in TEXT.items())
    header = (f'<header class="top"><a class="brand" href="{url(lang)}"><span class="mark">{"<i></i>" * 9}</span>'
              f'{esc(site["title"])}</a><div class="tools"><label class="sr" for="lang">{t["language"]}</label>'
              f'<select id="lang" onchange="location.href=this.value">{options}</select>'
              f'<button type="button" onclick="toggleTheme()" aria-label="{t["theme"]}" title="{t["theme"]}">{SUN}</button>'
              "</div></header>")
    alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="{url(code, path)}">' for code in TEXT)
    return (f'<!doctype html>\n<html lang="{lang}" data-theme="dark">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{title}</title>\n'
            f'<meta name="color-scheme" content="dark light">\n{alternates}\n<script>{THEME_JS}</script>\n'
            f'<link rel="stylesheet" href="/assets/site.css">\n</head>\n<body>\n<main>\n{header}\n{body}\n'
            f'<footer><span>© {site["year"]} {esc(site["developer"])}</span><a href="mailto:{site["email"]}">{site["email"]}</a></footer>\n'
            f'</main>\n<script>{TOGGLE_JS}</script>\n</body>\n</html>\n')


def section(title, *paragraphs):
    return f"<h2>{title}</h2>\n" + "".join(f"<p>{p}</p>\n" for p in paragraphs if p)


def privacy(game, cfg, lang):
    t = TEXT[lang]
    parts = [section(t["device_h"], t["device"])]
    ads = [t["ads"].format(store=esc(store), network=esc(net["name"]), company=esc(net["company"]),
                           privacy=net["privacy"], partner=net["partner"])
           for store, net in ((s, cfg["ad_networks"][k]) for s, k in game.get("ads", {}).items())]
    if ads:
        parts.append(section(t["ads_h"], *ads, t["no_ads"] if len(ads) < len(game["stores"]) else ""))
    if game.get("purchases"):
        parts.append(section(t["buy_h"], t["buy"].format(stores=t["and"].join(map(esc, game["stores"])))))
    parts += [section(t["kids_h"], t["kids"].format(name=esc(game["name"]))), section(t["rights_h"], t["rights"]),
              section(t["security_h"], t["security"]), section(t["changes_h"], t["changes"])]
    return (f'<h1>{t["title"].format(name=esc(game["name"]))}</h1>\n<p class="meta">{t["effective"].format(date=date_text(game["effective"], lang))}</p>\n'
            f'<p class="lead">{t["summary"]}</p>\n' + "".join(parts))


def home(cfg, lang):
    t = TEXT[lang]
    cards = "".join(
        f'<li class="game"><img src="/assets/games/{g["key"]}.png" alt="" width="64" height="64">'
        f'<div><h3>{esc(g["name"])}</h3><p>{esc(g["tagline"][lang])}</p>'
        f'<div class="links"><a href="{url(lang, g["key"] + "/privacy/")}">{t["policy"]}</a></div></div></li>\n'
        for g in cfg["games"])
    return f'<h1>{esc(cfg["site"]["title"])}</h1>\n<p class="meta">{t["tagline"]}</p>\n<h2>{t["games"]}</h2>\n<ul class="games">\n{cards}</ul>'


def write(rel, text):
    bad = FORBIDDEN.findall(re.sub(r"<[^>]+>", "", text))
    if bad:
        raise SystemExit(f"{rel}: forbidden typography {sorted(set(bad))}")
    path = ROOT / rel / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", path.relative_to(ROOT))


def main():
    cfg = json.loads((ROOT / "games.json").read_text(encoding="utf-8"))
    site = cfg["site"]
    for lang in TEXT:
        base = "" if lang == DEFAULT else f"{lang}/"
        write(base or ".", page(lang, "", esc(site["title"]), home(cfg, lang), site))
        for g in cfg["games"]:
            path = f'{g["key"]}/privacy/'
            write(base + path, page(lang, path, TEXT[lang]["title"].format(name=esc(g["name"])), privacy(g, cfg, lang), site))


if __name__ == "__main__":
    main()
