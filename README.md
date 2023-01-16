# Projektna-naloga-Prog1-
Projektna naloga iz zajema in analize podatkov pri predmetu Programiranje1


Zajetje podatkov o gorah v slovenskih Alpah (Julijske Alpe, Karavanke, Kamniško-Savinjske Alpe), dostopnih na https://www.hribi.net/gorovja

Podatke razvrstimo v 3 tabele (.csv, pa tudi .json), saj je za vsako goro možnih vsaj eno izhodišče in vsaj ena vrsta vrha. Za vsako goro se tako generira poseben id, ki se tako ponovi v vseh 3 tabelah, da podatki ostanejo povezani med seboj:
1. V prvi tabeli imamo opravka z gorami v 3 gorovjih, v bistvu za vsako gorovje zgeneriramo svojo tabelo. V njej so podatki:
    - id
    - ime gore
    - v katerem delu Alp se nahaja (Julijske Alpe, Kamniško Savinjske Alpe ali Karavanke)
    - višina
    - priljubljenost lokacije (v %)
    - koordinate vrha (če podatek obstaja)
2. Skupna tabela z vrsto vrha:
    - id
    - vrsta (vrh, koča, bivak ...)
3. skupna tabela z izhodišči:
    - id
    - ime izhodišča
    - čas poti
    - zahtevnost vsake poti
    - ime poti
    - višina izhodišča
    - višinska razlika med izhodiščem in vrhom

Analiza:
- razvrstitev glede na priljubljenost
- koliko gora ima več kot eno izhodišče?
- katere so vse možne zahtevnosti poti?
- razvrstitev po padajoči višinski razliki med izhodiščem in vrhom
- katere so vse vrste vrhov in koliko jih je (število koč in bivakov ter število vrhov)
- izris lokacij kot na zemljevidu

Hipoteze:
- Ali je višina gore povezana z njeno priljubljenostjo?
- Čas poti je povezan z višinsko razliko med izhodiščem in vrhom gore.
- Več kot 75 % gora ima več kot eno izhodišče (če podatek o izhodiščih manjka, predpostavimo, da je eno samo)
- Vrhov je več kot koč in bivakov.

