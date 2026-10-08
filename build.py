"""Builds the static site from games.json: the home page and one privacy page per game.

Add a game: append an entry to games.json, run `python build.py`, commit, push.
Typography: straight double quotes "" and the plain hyphen-minus only (checked on build).
"""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
FORBIDDEN = re.compile("[–—«»“”„‘’…]")

PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<main>
{body}
<footer>{developer} · <a href="mailto:{email}">{email}</a></footer>
</main>
</body>
</html>
"""

TEXT = {
    "en": {
        "policy": "Privacy policy",
        "effective": "Effective",
        "summary": "No account, no sign-up and no server of our own. Your progress and settings stay on your device. Only the ad network and the app store receive the data they need to show ads and process purchases.",
        "device_h": "Data on your device",
        "device": "Puzzle progress, statistics, streaks, hints, settings and the items you own. Android may include them in your device backup if backup is on; we never receive this data.",
        "ads_h": "Advertising",
        "ads": "The {store} version shows ads through {network} ({company}). To show and measure ads and to prevent fraud, it may process the advertising ID, IP address and approximate location, device and app information, ad interactions and diagnostics. In the EEA, the UK, Switzerland and some US states the app asks for your consent first and lets you change it later in Settings. You can reset the advertising ID or opt out of personalized ads in your device settings. See the <a href=\"{privacy}\">{company} privacy policy</a> and <a href=\"{partner}\">how it uses data from partner apps</a>.",
        "no_ads": "Other versions show no ads.",
        "buy_h": "Purchases",
        "buy": "Purchases are processed by {stores} under their own terms. We only receive a confirmation of which item you own and never see your payment details.",
        "kids_h": "Children",
        "kids": "{name} is not directed at children, and we do not knowingly collect data from children under 13.",
        "rights_h": "Your choices",
        "rights": "Uninstalling the app deletes its data from your device. We hold no personal data, so there is nothing for us to export or erase. Requests about advertising data go to the ad network, requests about purchases go to the app store.",
        "security_h": "Security",
        "security": "The ad and store SDKs send data encrypted (TLS).",
        "changes_h": "Changes",
        "changes": "We update this page and its effective date when something changes.",
        "contact_h": "Contact",
        "games": "Games",
        "other_lang": "Русский",
    },
    "ru": {
        "policy": "Политика конфиденциальности",
        "effective": "Действует с",
        "summary": "Без аккаунта, регистрации и собственного сервера. Прогресс и настройки хранятся только на вашем устройстве. Данные получают лишь рекламная сеть и магазин приложений - ровно то, что нужно для показа рекламы и покупок.",
        "device_h": "Данные на устройстве",
        "device": "Прогресс, статистика, серии, подсказки, настройки и купленные предметы. Android может включить их в резервную копию устройства, если она включена; мы эти данные не получаем.",
        "ads_h": "Реклама",
        "ads": "Версия для {store} показывает рекламу через {network} ({company}). Для показа и учёта рекламы и защиты от мошенничества может обрабатываться рекламный идентификатор, IP-адрес и приблизительное местоположение, сведения об устройстве и приложении, взаимодействие с рекламой и диагностика. В ЕЭЗ, Великобритании, Швейцарии и некоторых штатах США приложение сначала спрашивает согласие, изменить его можно в настройках. Рекламный идентификатор можно сбросить, а персонализацию отключить в настройках устройства. Подробнее: <a href=\"{privacy}\">политика конфиденциальности {company}</a> и <a href=\"{partner}\">как используются данные из приложений партнёров</a>.",
        "no_ads": "Другие версии рекламу не показывают.",
        "buy_h": "Покупки",
        "buy": "Покупки обрабатывают {stores} по своим правилам. Мы получаем только подтверждение того, каким предметом вы владеете, и не видим платёжных данных.",
        "kids_h": "Дети",
        "kids": "{name} не предназначена для детей, и мы сознательно не собираем данные детей младше 13 лет.",
        "rights_h": "Ваш выбор",
        "rights": "Удаление приложения удаляет его данные с устройства. Мы не храним персональных данных, поэтому выгружать или удалять у нас нечего. Вопросы о рекламных данных - к рекламной сети, о покупках - к магазину приложений.",
        "security_h": "Безопасность",
        "security": "Рекламный SDK и SDK магазина передают данные в зашифрованном виде (TLS).",
        "changes_h": "Изменения",
        "changes": "При изменениях мы обновляем эту страницу и дату вступления в силу.",
        "contact_h": "Связь",
        "games": "Игры",
        "other_lang": "English",
    },
}


def section(title, *paragraphs):
    return f"<h2>{title}</h2>\n" + "".join(f"<p>{p}</p>\n" for p in paragraphs if p)


def privacy_body(game, cfg, lang):
    t, site = TEXT[lang], cfg["site"]
    esc = html.escape
    parts = [section(t["device_h"], t["device"])]
    ads = []
    for store, key in game.get("ads", {}).items():
        net = cfg["ad_networks"][key]
        ads.append(t["ads"].format(store=esc(store), network=esc(net["name"]), company=esc(net["company"]),
                                   privacy=net["privacy"], partner=net["ads"]))
    if ads:
        if len(ads) < len(game["stores"]):
            ads.append(t["no_ads"])
        parts.append(section(t["ads_h"], *ads))
    if game.get("purchases"):
        stores = (" и " if lang == "ru" else " and ").join(map(esc, game["stores"]))
        parts.append(section(t["buy_h"], t["buy"].format(stores=stores)))
    parts += [
        section(t["kids_h"], t["kids"].format(name=esc(game["name"]))),
        section(t["rights_h"], t["rights"]),
        section(t["security_h"], t["security"]),
        section(t["changes_h"], t["changes"]),
        section(t["contact_h"], f'{esc(site["developer"])}, <a href="mailto:{site["email"]}">{site["email"]}</a>'),
    ]
    return (f'<section id="{lang}">\n<h1>{esc(game["name"])}: {t["policy"].lower() if lang == "ru" else t["policy"]}</h1>\n'
            f'<p class="meta">{t["effective"]} {game["effective"]}</p>\n<p>{t["summary"]}</p>\n' + "".join(parts) + "</section>\n")


def write(path, text):
    bad = FORBIDDEN.findall(re.sub(r"<[^>]+>", "", text))
    if bad:
        raise SystemExit(f"{path}: forbidden typography {sorted(set(bad))}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", path.relative_to(ROOT))


def main():
    cfg = json.loads((ROOT / "games.json").read_text(encoding="utf-8"))
    site = cfg["site"]
    esc = html.escape
    for game in cfg["games"]:
        body = (f'<header><a class="brand" href="/">{esc(site["title"])}</a>\n'
                f'<nav class="lang"><a href="#en">English</a><a href="#ru">Русский</a></nav></header>\n'
                + privacy_body(game, cfg, "en") + privacy_body(game, cfg, "ru"))
        write(ROOT / game["key"] / "privacy" / "index.html",
              PAGE.format(lang="en", title=f'{esc(game["name"])} - Privacy policy', description=f'{esc(game["name"])} privacy policy',
                          body=body, developer=esc(site["developer"]), email=site["email"]))
    items = "".join(
        f'<li><b>{esc(g["name"])}</b><br>{esc(g["tagline_en"])}<br><span class="meta">{esc(g["tagline_ru"])}</span><br>'
        f'<a href="/{g["key"]}/privacy/">Privacy policy</a> · <a href="/{g["key"]}/privacy/#ru">Политика конфиденциальности</a></li>\n'
        for g in cfg["games"])
    body = (f'<header><h1>{esc(site["title"])}</h1>\n<p class="meta">{esc(site["tagline_en"])} {esc(site["tagline_ru"])}</p></header>\n'
            f'<h2>Games</h2>\n<ul class="games">\n{items}</ul>\n')
    write(ROOT / "index.html", PAGE.format(lang="en", title=esc(site["title"]), description=esc(site["tagline_en"]),
                                          body=body, developer=esc(site["developer"]), email=site["email"]))


if __name__ == "__main__":
    main()
