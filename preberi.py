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
    r'form.*?id=(?P<id>.*?)".*?'
    r'<h1>(?P<ime>.*?)<\/h1>.'
    r'*?Država:<\/b>.*?>'
    r'(?P<drzava>.*?)<.*?'
    r'Gorovje:<\/b>.*?>(?P<gorovje>.*?)<.*?'
    r'Višina:\D*(?P<visina>\d*).*?'
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
    r'<a href="(?P<url>.*?)">(?P<izhodisce>.*?)\s-.*?'
    r'<a.*?>(?P<cas>.*?)<.*?<a.*?'
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

# za ureditev podatkov v slovarju (niz s številko v int in podobno)
def uredi_slovar(slovar, html_vsebina, i):
    # id-ju dodamo 1/2/3 (odvisno od gorovja), da se gotovo ne ponovi
    slovar['id'] = i + int(''.join(filter(str.isdigit, slovar['id'])))
    slovar['visina'] = int(slovar['visina'])
    slovar['vrsta'] = slovar['vrsta'].lstrip()
    slovar['priljubljenost'] = int(slovar['priljubljenost'].lstrip())
    # ker nima vsaka gora podanih koordinat:
    koordinate = re.search(vzorec_koordinate, html_vsebina)
    if koordinate is None:
        slovar['koordinate'] = 'Brez podatka'
    else:
        slovar['koordinate'] = koordinate.group('koordinate').replace('&nbsp;',' ')
    return slovar

# za ureditev izhodišč, ki jih vse shranimo skupaj v poseben slovar
def uredi_izhodisca(html_vseh_izhodisc, id, visina):
    # izhodišča so podana kot odsek html-ja. Moramo jih ločiti in izpisati ven podatke v obliki slovarja, kjer je ključ izhodišče, vsebina pa poti, čas in zahtevnost
    bloki_izhodisc = re.findall(vzorec_html_izhodisca, html_vseh_izhodisc)
    izhodisca = []
    for blok in bloki_izhodisc:
        # za vsako izhodišče preberemo podatke. Najprej dodamo id, ki je enak kot id gore, na katero lahko gremo iz tega izhodišča; ostali podatki: ime izhodišča, čas poti do vrha, zahtevnost, ime poti, višina izhodišča, višinska razlika med izhodiščem in vrhom
        # za višino je treba pogledat v novo html stran, ampak jih nisem shranjevala, ker bi bilo teh strani veliko, tako pač prebiranje traja malo dlje ...
        pot = {'id': id}
        pot_brez_id = vzorec_izhodisca.search(blok).groupdict()
        pot.update(pot_brez_id)
        pot['izhodisce'] = pot['izhodisce'].strip()
        ime_poti = vzorec_ime_poti.search(blok)
        if ime_poti:
            pot['pot'] = ime_poti.group('pot')
        cas = re.findall(r'\d+', pot['cas'])
        if len(cas) == 1:
            pot['cas'] = int(cas[0])*60
        else:
            pot['cas'] = int(cas[0])*60 + int(cas[-1])
        pot["visinaizhodisca"] = int(vzorec_visina_izhodisca.search(requests.get(url_hribi+pot['url']).text).group('visinaizh'))
        pot['visinskarazlika'] = visina - pot["visinaizhodisca"]
        pot.pop('url')
        izhodisca.append(pot)
    return izhodisca

# uredimo še vrsto (vrha, bivak, koča ...)
def uredi_vrsto(niz, id):
    niz = niz.replace(',', ' ')
    seznam = []
    for vrsta in niz.split():
        seznam.append({'id': id, 'vrsta': vrsta})
    return seznam

# za shranjevanje strani o vsaki gori posebej in prebranje podatkov iz nje
def shrani_strani_gora(slovar_ime_url, i):
    # v slovarju imamo podano ime gore in url, ki vodi k njenemu opisu in ostalimi podatki
    url = url_hribi + slovar_ime_url['url'] # url te gore
    ime = slovar_ime_url['ime'].replace(' ','_').replace('/','_') + '.html' # ime .html, kamor shranimo stran s tem url
    orodja.shrani_spletno_stran(url, ime, mapa_gorovij[i])
    html_vsebina = orodja.vsebina_datoteke(os.path.join(mapa_gorovij[i], ime))
    slovar = uredi_slovar(vzorec_podatki.search(html_vsebina).groupdict(), html_vsebina, i) # preberemo podatke in shranimo v slovar, ki ga uredimo s to funkcijo
    # DODANO: vzamemo le slovenske gore, ker me italijanske in avstrijske ne zanimajo:)
    if slovar['drzava'] == 'Slovenija':
        izhodisca = uredi_izhodisca(slovar['tabelapoti'], slovar["id"], slovar['visina'])
        # posebej naredimo še tabelo z izhodišči ter z vrstami vrha; imajo skupen id z goro, da ostanejo podatki povezani
        vrsta = uredi_vrsto(slovar['vrsta'], slovar['id'])
        slovar.pop('tabelapoti')
        slovar.pop('vrsta')
        # iz originalnega slovarja odstranimo ta dva podatka, ker sta v posebej tabelah
        return slovar, izhodisca, vrsta
    else:
        return None, None, None

# za prebranje podatkov iz posamezne strani, a je ne shranimo (časovno potratno in stalo requesta dostop, zato te funkcije ne nucamo)
# def preberi_strani_gora(slovar_ime_url):
#     url = url_hribi + slovar_ime_url['url']
#     try:
#         print("Izpisujem podatke o: " + slovar_ime_url['ime'])
#         vsebina = requests.get(url)
#     except requests.exceptions.ConnectionError:
#         print('stran ne obstaja!')
#     else:
#         html_vsebina = vsebina.text
#         slovar = uredi_slovar(vzorec_podatki.search(html_vsebina).groupdict(), html_vsebina, i)
#         izhodisca = uredi_izhodisca(slovar['tabelapoti'], slovar["id"], slovar['visina'])
#         vrsta = uredi_vrsto(slovar['vrsta'], slovar['id'])
#         slovar.pop('tabelapoti')
#         slovar.pop('vrsta')
#         return slovar, izhodisca, vrsta


#####################################################
# glavna funkcija, ki zbere in shrani podatke:
#####################################################
izhodisca = [] # izhodišča in vrste bomo shranili vsa v eno datoteko
vrsta = []

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
        slovar, izhodisca_gore, vrsta_lokacije = shrani_strani_gora(slovar_ime_url, i)
    # 2. način - iz vsake strani le preberemo podatke in je ne shranimo, ampak potem vsakič prebira znova in to ni kul ...
        # slovar = preberi_strani_gora(slovar_ime_url)
    # dobljen slovar dodamo v seznam podatkov:
        if slovar != None:
            slovar.pop('drzava')
            seznam_podatkov.append(slovar)
            izhodisca += izhodisca_gore
            vrsta += vrsta_lokacije

    # zapišimo to v csv in json datoteko:
    orodja.zapisi_csv(seznam_podatkov, seznam_podatkov[0].keys(), os.path.join(mapa_gorovij[i], csv_gorovij[i]))
    orodja.zapisi_json(seznam_podatkov, os.path.join(mapa_gorovij[i], json_gorovij[i]))

orodja.zapisi_csv(izhodisca, izhodisca[0].keys(), 'podatki\\izhodisca.csv')
orodja.zapisi_json(izhodisca, 'podatki\\izhodisca.json')

orodja.zapisi_csv(vrsta, vrsta[0].keys(), 'podatki\\vrsta.csv')
orodja.zapisi_json(vrsta, 'podatki\\vrsta.json')