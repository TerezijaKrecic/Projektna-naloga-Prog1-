import requests
import re
import orodja
import os

# glavna stran:
url_hribi = 'https://www.hribi.net'

# url glavnih treh strani:
url_julijske_alpe = 'https://www.hribi.net/gorovje/julijske_alpe/1'
url_karavanke = 'https://www.hribi.net/gorovje/karavanke/11'
url_kamn_sav_alpe = 'https://www.hribi.net/gorovje/kamnisko_savinjske_alpe/3'

# pot do mape, kjer shranimo posamezne podatke
mapa_julijske_alpe = 'podatki\\julijske_alpe'
mapa_karavanke = 'podatki\\karavanke'
mapa_kamn_sav_alpe = 'podatki\\kamn_sav_alpe'

# ime html datotek z vsebino glavnih treh strani (spredaj je AA, da se pojavi na vrhu strani)
datoteka_julijske_alpe = 'A_julijske_alpe.html'
datoteka_karavanke = 'A_karavanke.html'
datoteka_kamn_sav_alpe = 'A_kamn_sav_alpe.html'

csv_julijske_alpe = 'A_julijske_alpe.csv'
json_julijske_alpe = 'A_julijske_alpe.json'

# Shranimo glavne spletne strani o gorah v svoje mape:
orodja.shrani_spletno_stran(url_julijske_alpe, datoteka_julijske_alpe, mapa_julijske_alpe)
orodja.shrani_spletno_stran(url_karavanke, datoteka_karavanke, mapa_karavanke)
orodja.shrani_spletno_stran(url_kamn_sav_alpe, datoteka_kamn_sav_alpe, mapa_kamn_sav_alpe)

# vzorci za iskanje:
vzorec_blok_gora = re.compile(
    r'<tr class="vr.*?&nbsp;m',
    re.DOTALL
)
vzorec_ime_in_url = re.compile(
    r'<tr class="vr.*?<a href="(?P<url>.*?)"'
    r'>(?P<ime>.+?)<.*?\1"',
    re.DOTALL
)
vzorec_podatki = re.compile(
    r'<h1>(?P<ime>.*?)<\/h1>.'
    r'*?Država:<\/b>.*?>'
    r'(?P<država>.*?)<.*?'
    r'Gorovje:<\/b>.*?>(?P<gorovje>.*?)<.*?'
    r'Višina:\D*(?P<višina>\d*).*?',
    re.DOTALL
)
vzorec_koordinate = re.compile(r'Širina.*?span.*?>(?P<koordinate>.*?)<', re.DOTALL)

###################
# julijske alpe
###################

# Niz s html vsebino glavne strani julijskih alp:
julijske_alpe_vsebina = orodja.vsebina_datoteke(os.path.join(mapa_julijske_alpe, datoteka_julijske_alpe))

# izluščimo odsek html-ja za posamezno goro:
seznam_html_podatkov = re.findall(vzorec_blok_gora, julijske_alpe_vsebina)

# iz posameznega odseka preberemo url s podrobnostmi in ta html shranimo v isto mapo pod imenom 'ime_gore'.html
seznam_podatkov = []
for blok in seznam_html_podatkov:
    slovar_ime_url = vzorec_ime_in_url.search(blok).groupdict()
    url = url_hribi + slovar_ime_url['url']
    ime = slovar_ime_url['ime'].replace(' ','_').replace('/','_') + '.html'
    orodja.shrani_spletno_stran(url, ime, mapa_julijske_alpe)
    # zberimo koristne podatke:
    html_vsebina = orodja.vsebina_datoteke(os.path.join(mapa_julijske_alpe, ime))
    slovar = vzorec_podatki.search(html_vsebina).groupdict()
    slovar['višina'] = int(slovar['višina'])
    koordinate = re.search(vzorec_koordinate, html_vsebina)
    if koordinate is None:
        slovar['koordinate'] = 'Brez podatka'
    else:
        slovar['koordinate'] = koordinate.group('koordinate').replace('&nbsp;',' ')
    seznam_podatkov.append(slovar)

# zapišimo to v csv in json datoteko:
orodja.zapisi_csv(seznam_podatkov, seznam_podatkov[0].keys(), os.path.join(mapa_julijske_alpe, csv_julijske_alpe))
orodja.zapisi_json(seznam_podatkov, os.path.join(mapa_julijske_alpe, json_julijske_alpe))
