import requests
import re
import orodja
import os

vzorec = '<tr class="trG0"><td class="tdG"><a href="/izlet/konec_ceste_na_pokljuki_triglav_cez_planiko_in_mali_triglav/1/1/133">Konec ceste na Pokljuki - Triglav (čez Planiko in Mali Triglav)</a></td><td class="tdG"><a href="/izlet/konec_ceste_na_pokljuki_triglav_cez_planiko_in_mali_triglav/1/1/133">6 h</a></td><td class="tdG"><a href="/izlet/konec_ceste_na_pokljuki_triglav_cez_planiko_in_mali_triglav/1/1/133">zelo zahtevna označena pot</a></td></tr>'

vzorec_izhodisca = re.compile(
    r'<a.*?> (?P<izhodisce>.*?)\s-.*?',
   #r'\((?P<pot>.*?)\)<.*?'
    #r'<a.*?>(?P<cas>.*?)<.*?<a.*?'
    #r'>(?P<zahtevnost>.*?)<',
    re.DOTALL
)
pot = vzorec_izhodisca.search(vzorec).groupdict()
print([pot])