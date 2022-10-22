import requests
import re
import orodja

url_julijske_alpe = 'https://www.hribi.net/gorovje/julijske_alpe/1'
url_karavanke = 'https://www.hribi.net/gorovje/karavanke/11'
url_kamn_sav_alpe = 'https://www.hribi.net/gorovje/kamnisko_savinjske_alpe/3'

# Shranimo glavne spletne strani o gorah v svoje mape:
orodja.shrani_spletno_stran(url_julijske_alpe, 'julijske_alpe.html', 'podatki\\julijske_alpe')
orodja.shrani_spletno_stran(url_karavanke, 'karavanke.html', 'podatki\\karavanke')
orodja.shrani_spletno_stran(url_kamn_sav_alpe, 'kamn_sav_alpe.html', 'podatki\\kamn_sav_alpe')