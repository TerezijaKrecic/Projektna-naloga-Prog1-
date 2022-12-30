import requests
import re
import orodja
import os

# glavna stran:
url_hribi = 'https://www.hribi.net'

# url glavnih treh strani:
url_gorovij = ['https://www.hribi.net/gorovje/julijske_alpe/1', 'https://www.hribi.net/gorovje/karavanke/11', 'https://www.hribi.net/gorovje/kamnisko_savinjske_alpe/3']

# pot do mape, kjer shranimo posamezne podatke
mapa_gorovij = ['podatki\\julijske_alpe', 'podatki\\karavanke', 'podatki\\kamn_sav_alpe']

# ime html datotek z vsebino glavnih treh strani (spredaj je AA, da se pojavi na vrhu strani)
datoteka_gorovij = ['A_julijske_alpe.html', 'A_karavanke.html', 'A_kamn_sav_alpe.html']

# ime csv datotek z izluščenimi podatki vsake od treh gravnih strani (spredaj je AA, da se pojavi na vrhu strani)
csv_gorovij = ['A_julijske_alpe.csv', 'A_karavanke.csv', 'A_kamn_sav_alpe.csv']

# ime json datotek z izluščenimi podatki vsake od treh gravnih strani (spredaj je AA, da se pojavi na vrhu strani)
json_gorovij = ['A_julijske_alpe.json', 'A_karavanke.json', 'A_kamn_sav_alpe.json']

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
    r'Višina:\D*(?P<višina>\d*).*?'
    r'<b>Vrsta:</b>(?P<vrsta>.*?)</div>.*?'
    r'<b>Priljubljenost:</b>.*?(?P<priljubljenost>\d*)%.*?'
    r'<table class="TPoti".*?</tr>\s*(?P<tabelapoti>.*?)\s*</table>',
    re.DOTALL
)
vzorec_html_izhodisca = re.compile(
    r'<tr.*?</tr>',
    re.DOTALL
)
vzorec_izhodisca = re.compile(
    r'<a href="(?P<url>.*?)">(?P<izhodišče>.*?)\s-.*?'
    r'<a.*?>(?P<čas>.*?)<.*?<a.*?'
    r'>(?P<zahtevnost>.*?)<',
    re.DOTALL
)
vzorec_ime_poti = re.compile(r'<a.*?\s-.*?\((?P<pot>.*?)\)<', re.DOTALL)
vzorec_visina_izhodisca = re.compile(r'<b>Izhodišče:.*?\((?P<visinaizh>\d*?) ', re.DOTALL)
vzorec_koordinate = re.compile(r'Širina.*?span.*?>(?P<koordinate>.*?)<', re.DOTALL)

###################
# ZBEREMO PODATKE
###################

# POMOŽNE FUNKCIJE:

# za ureditev podatkov (niz s številko v int in podobno)
def uredi(slovar, html_vsebina):
    slovar['višina'] = int(slovar['višina'])
    slovar['vrsta'] = slovar['vrsta'].lstrip()
    slovar['priljubljenost'] = int(slovar['priljubljenost'].lstrip())
    slovar['priljubljenost v %'] = slovar.pop('priljubljenost')
    # izhodišča so podana kot odsek html-ja. Moramo jih ločiti in izpisati ven podatke v obliki slovarja, kjer je ključ izhodišče, vsebina pa poti, čas in zahtevnost
    slovar['izhodišča in poti'] = slovar.pop('tabelapoti')
    bloki_izhodisc = re.findall(vzorec_html_izhodisca, slovar['izhodišča in poti'])
    izhodisca = []
    for blok in bloki_izhodisc:
        pot = vzorec_izhodisca.search(blok).groupdict()
        ime_poti = vzorec_ime_poti.search(blok)
        if ime_poti:
            pot['pot'] = ime_poti.group('pot')
        cas = re.findall(r'\d+', pot['čas'])
        pot['čas v min'] = pot.pop('čas')
        if len(cas) == 1:
            pot['čas v min'] = int(cas[0])*60
        else:
            pot['čas v min'] = int(cas[0])*60 + int(cas[-1])
        pot["višina izhodišča"] = int(vzorec_visina_izhodisca.search(requests.get(url_hribi+pot['url']).text).group('visinaizh'))
        pot['višinska razlika'] = slovar['višina'] - pot["višina izhodišča"]
        pot.pop('url')
        izhodisca.append(pot)
    slovar['izhodišča in poti'] = izhodisca
    # ker nima vsaka gora podanih koordinat:
    koordinate = re.search(vzorec_koordinate, html_vsebina)
    if koordinate is None:
        slovar['koordinate'] = 'Brez podatka'
    else:
        slovar['koordinate'] = koordinate.group('koordinate').replace('&nbsp;',' ')
    return slovar

# za shranjevanje strani o vsaki gori posebej in prebranje podatkov iz nje
def shrani_strani_gora(slovar_ime_url, i):
    url = url_hribi + slovar_ime_url['url']
    ime = slovar_ime_url['ime'].replace(' ','_').replace('/','_') + '.html'
    orodja.shrani_spletno_stran(url, ime, mapa_gorovij[i])
    html_vsebina = orodja.vsebina_datoteke(os.path.join(mapa_gorovij[i], ime))
    slovar = vzorec_podatki.search(html_vsebina).groupdict()
    slovar = uredi(slovar, html_vsebina)
    return slovar

# za prebranje podatkov iz posamezne strani, a je ne shranimo (časovno potratno in stalo requesta dostop, zato je ne nucamo)
def preberi_strani_gora(slovar_ime_url):
    url = url_hribi + slovar_ime_url['url']
    try:
        print("Izpisujem podatke o: " + slovar_ime_url['ime'])
        vsebina = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
    else:
        html_vsebina = vsebina.text
        slovar = vzorec_podatki.search(html_vsebina).groupdict()
        slovar = uredi(slovar, html_vsebina)
        return slovar

#####################################################
# glavna funkcija, ki zbere in shrani podatke:
#####################################################
for i in range(len(url_gorovij)):
    # Shranimo tri glavne spletne strani o gorah v svoje mape:
    orodja.shrani_spletno_stran(url_gorovij[i], datoteka_gorovij[i], mapa_gorovij[i])

    # Niz s html vsebino glavne strani posameznega gorovja:
    gorovje_vsebina = orodja.vsebina_datoteke(os.path.join(mapa_gorovij[i], datoteka_gorovij[i]))

    # izluščimo odsek html-ja za posamezno goro:
    seznam_html_podatkov = re.findall(vzorec_blok_gora, gorovje_vsebina)

    # iz posameznega odseka preberemo url s podrobnostmi in poiščemo podatke, ki jih v obliki slovarja shranimo v seznam:
    seznam_podatkov = []
    for html_gore in seznam_html_podatkov:
        slovar_ime_url = vzorec_ime_in_url.search(html_gore).groupdict()
    # 1. način - s shranjevanjem vsake strani (to pomeni smetenje mape s podatki, ampak bolje kot 2. način):
        slovar = shrani_strani_gora(slovar_ime_url, i)
    # 2. način - iz vsake strani le preberemo podatke in je ne shranimo, ampak potem vsakič prebira znova in to ni kul ...
        # slovar = preberi_strani_gora(slovar_ime_url)
    # dobljen slovar dodamo v seznam podatkov:
        seznam_podatkov.append(slovar)

    # zapišimo to v csv in json datoteko:
    orodja.zapisi_csv(seznam_podatkov, seznam_podatkov[0].keys(), os.path.join(mapa_gorovij[i], csv_gorovij[i]))
    orodja.zapisi_json(seznam_podatkov, os.path.join(mapa_gorovij[i], json_gorovij[i]))
    # ker sem pozabla odstranit url od izhodišč:



