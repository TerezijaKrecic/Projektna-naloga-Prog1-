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


###################
# julijske alpe
###################

# Niz s html vsebino glavne strani julijskih alp:
julijske_alpe_vsebina = orodja.vsebina_datoteke(os.path.join(mapa_julijske_alpe, datoteka_julijske_alpe))

# izluščimo odsek html-ja za posamezno goro:
seznam_html_podatkov = re.findall(vzorec_blok_gora, julijske_alpe_vsebina)

# iz posameznega odseka preberemo url s podrobnostmi in ta html shranimo v isto mapo pod imenom 'ime_gore'.html
for blok in seznam_html_podatkov:
    slovar_ime_url = vzorec_ime_in_url.search(blok).groupdict()
    orodja.shrani_spletno_stran(url_hribi + slovar_ime_url['url'], slovar_ime_url['ime'].replace(' ','_').replace('/','_') + '.html', mapa_julijske_alpe)
