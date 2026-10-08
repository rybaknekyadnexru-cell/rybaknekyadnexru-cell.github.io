"""Builds the static site from games.json: a home page and, per game, a game page, a privacy policy and terms of use,
in every language.

URLs: English at /, /<game>/, /<game>/privacy/, /<game>/terms/ ; other languages under /<lang>/.
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
        "terms_link": "Terms of use",
        "terms_title": "{name}: terms of use",
        "terms_lead": "By installing or playing {name} you accept these terms. They are short on purpose.",
        "t_license_h": "Your license",
        "t_license": "We give you a personal, non-exclusive, non-transferable license to install and play {name} on devices you own or control. Do not copy, resell, reverse engineer or redistribute the app or its content, except where the law allows it.",
        "t_buy_h": "Purchases and subscriptions",
        "t_buy": "Items and subscriptions are sold and billed by {stores} under their own terms, at the price shown before you pay. A subscription renews automatically each period until you cancel it in the store's subscription settings; cancelling stops the next renewal, and the benefit lasts until the end of the paid period. Refunds follow the store's refund policy.",
        "t_items_h": "Virtual items",
        "t_items": "Hints, picture albums, themes, backgrounds and other in-game items have no cash value, cannot be exchanged for money and are not transferable. Items you buy are restored with the store's restore option on the same store account.",
        "t_ads_h": "Advertising",
        "t_ads": "The free version shows ads. A rewarded video is always your choice and gives the reward shown on the button.",
        "t_use_h": "Fair play",
        "t_use": "Do not cheat the reward or purchase systems, tamper with the app, or use it to break the law. We may withhold rewards obtained this way.",
        "t_warranty_h": "No warranty",
        "t_warranty": "The app is provided as is. We work to keep it free of bugs and data loss, but we cannot promise it will always be available or error-free. Progress lives on your device: back it up with Android's backup if you want to keep it across devices.",
        "t_liability_h": "Liability",
        "t_liability": "To the extent the law allows, we are not liable for indirect or consequential damages, and our total liability is limited to the amount you paid for the app in the twelve months before the claim. Nothing here limits rights you have as a consumer that cannot be waived.",
        "t_changes_h": "Changes",
        "t_changes": "We may update these terms; the new version applies from its effective date. If you keep playing, you accept it.",
        "t_contact_h": "Contact",
        "t_contact": "Questions and support: <a href=\"mailto:{email}\">{email}</a>.",
        "play_h": "What is inside",
        "stores_h": "Where to get it",
        "soon": "Coming soon to {stores}.",
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
        "terms_link": "Условия использования",
        "terms_title": "{name}: условия использования",
        "terms_lead": "Устанавливая {name} или играя в неё, вы принимаете эти условия. Они короткие специально.",
        "t_license_h": "Лицензия",
        "t_license": "Мы даём вам личную, неисключительную и непередаваемую лицензию устанавливать {name} и играть в неё на своих устройствах. Не копируйте, не перепродавайте, не декомпилируйте и не распространяйте приложение и его содержимое, кроме случаев, разрешённых законом.",
        "t_buy_h": "Покупки и подписки",
        "t_buy": "Предметы и подписки продают и оплачивают {stores} по своим правилам и по цене, показанной до оплаты. Подписка продлевается автоматически каждый период, пока вы не отмените её в разделе подписок магазина; отмена останавливает следующее продление, а оплаченный период действует до конца. Возвраты - по правилам магазина.",
        "t_items_h": "Виртуальные предметы",
        "t_items": "Подсказки, альбомы картинок, темы, фоны и другие игровые предметы не имеют денежной стоимости, не обмениваются на деньги и не передаются другим. Купленное восстанавливается через восстановление покупок в том же аккаунте магазина.",
        "t_ads_h": "Реклама",
        "t_ads": "Бесплатная версия показывает рекламу. Ролик за награду - всегда ваш выбор, он даёт награду, указанную на кнопке.",
        "t_use_h": "Честная игра",
        "t_use": "Не обманывайте систему наград и покупок, не вмешивайтесь в работу приложения и не используйте его для нарушения закона. Награды, полученные так, мы можем не засчитать.",
        "t_warranty_h": "Без гарантий",
        "t_warranty": "Приложение предоставляется как есть. Мы следим, чтобы в нём не было ошибок и потерь данных, но не можем обещать, что оно всегда будет доступно и безошибочно. Прогресс хранится на устройстве: чтобы перенести его на другое, включите резервное копирование Android.",
        "t_liability_h": "Ответственность",
        "t_liability": "В пределах, разрешённых законом, мы не отвечаем за косвенный ущерб, а наша общая ответственность ограничена суммой, которую вы заплатили за приложение за двенадцать месяцев до претензии. Ничто здесь не ограничивает права потребителя, от которых нельзя отказаться.",
        "t_changes_h": "Изменения",
        "t_changes": "Мы можем обновлять эти условия; новая редакция действует с указанной даты. Продолжая играть, вы её принимаете.",
        "t_contact_h": "Контакты",
        "t_contact": "Вопросы и поддержка: <a href=\"mailto:{email}\">{email}</a>.",
        "play_h": "Что внутри",
        "stores_h": "Где скачать",
        "soon": "Скоро в {stores}.",
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


def terms(game, cfg, lang):
    t = TEXT[lang]
    name = esc(game["name"])
    stores = t["and"].join(map(esc, game["stores"]))
    email = cfg["site"]["email"]
    parts = [section(t["t_license_h"], t["t_license"].format(name=name))]
    if game.get("purchases"):
        parts += [section(t["t_buy_h"], t["t_buy"].format(stores=stores)), section(t["t_items_h"], t["t_items"])]
    if game.get("ads"):
        parts.append(section(t["t_ads_h"], t["t_ads"]))
    parts += [section(t["t_use_h"], t["t_use"]), section(t["t_warranty_h"], t["t_warranty"]),
              section(t["t_liability_h"], t["t_liability"]), section(t["t_changes_h"], t["t_changes"]),
              section(t["t_contact_h"], t["t_contact"].format(email=email))]
    return (f'<h1>{t["terms_title"].format(name=name)}</h1>\n<p class="meta">{t["effective"].format(date=date_text(game["effective"], lang))}</p>\n'
            f'<p class="lead">{t["terms_lead"].format(name=name)}</p>\n' + "".join(parts))


def game_links(game, lang):
    t = TEXT[lang]
    return (f'<div class="links"><a href="{url(lang, game["key"] + "/privacy/")}">{t["policy"]}</a>'
            f'<a href="{url(lang, game["key"] + "/terms/")}">{t["terms_link"]}</a></div>')


def game_page(game, cfg, lang):
    t = TEXT[lang]
    stores = game.get("store_urls", {})
    live = "".join(f'<a href="{u}">{esc(s)}</a>' for s, u in stores.items())
    waiting = [s for s in game["stores"] if s not in stores]
    where = (f'<div class="links">{live}</div>\n' if live else "") + (
        f'<p class="meta">{t["soon"].format(stores=t["and"].join(map(esc, waiting)))}</p>\n' if waiting else "")
    features = "".join(f"<li>{esc(f)}</li>" for f in game.get("features", {}).get(lang, []))
    return (f'<div class="hero"><img src="/assets/games/{game["key"]}.png" alt="" width="96" height="96">'
            f'<div><h1>{esc(game["name"])}</h1><p class="meta">{esc(game["tagline"][lang])}</p></div></div>\n'
            + (f'<h2>{t["play_h"]}</h2>\n<ul class="features">{features}</ul>\n' if features else "")
            + f'<h2>{t["stores_h"]}</h2>\n{where}' + game_links(game, lang))


def home(cfg, lang):
    t = TEXT[lang]
    cards = "".join(
        f'<li class="game"><img src="/assets/games/{g["key"]}.png" alt="" width="64" height="64">'
        f'<div><h3><a href="{url(lang, g["key"] + "/")}">{esc(g["name"])}</a></h3><p>{esc(g["tagline"][lang])}</p>'
        f'{game_links(g, lang)}</div></li>\n'
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
            name = esc(g["name"])
            write(base + f'{g["key"]}/', page(lang, f'{g["key"]}/', name, game_page(g, cfg, lang), site))
            path = f'{g["key"]}/privacy/'
            write(base + path, page(lang, path, TEXT[lang]["title"].format(name=name), privacy(g, cfg, lang), site))
            path = f'{g["key"]}/terms/'
            write(base + path, page(lang, path, TEXT[lang]["terms_title"].format(name=name), terms(g, cfg, lang), site))


if __name__ == "__main__":
    main()
