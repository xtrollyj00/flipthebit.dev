---
title: "Cache me if you can #1: Čo je cache a prečo ju potrebujete"
date: "2024-11-26"
description: "Zistite, čo je CPU cache a prečo ju potrebujú pamäťové systémy. O dátovej lokalite a o plne asociatívnej, priamo mapovanej a množinovo asociatívnej cache."
slug: "co-je-cache"
tags:
  - "Cache me if you can"
  - "data locality"
  - "cache"
---

Môj profesor teoretickej informatiky raz poznamenal: "Čo hovoria IT profesionáli, keď nastane problém 
s výkonom? Pridajme ďalšiu cache! :smile:" Pri práci s pamäťovými systémami je bežné naraziť na saturáciu
priepustnosti alebo zastavenie pipeline spôsobené nepredvídateľnou a vysokou latenciou čítania a zápisu.
Implementácia cache pamätí dokáže vo väčšine prípadov tento bottleneck efektívne odstrániť.

Bohužiaľ, výkon systému je obmedzený jeho najslabšou komponentou. V moderných výpočtových systémoch
výkon procesorov škáloval mimoriadne dobre - od roku 1999 sa zvýšil približne 100-násobne.
Toto zlepšenie sa však netýka pamäťových systémov. Od roku 1999:
- kapacita DRAM sa zvýšila 128-násobne,
- priepustnosť DRAM sa zvýšila iba 20-násobne,
- latencia DRAM sa znížila len približne 1,2-násobne.

Práve preto je 40–70 % plochy moderných CPU čipov venovaných dátovým prepojeniam,
cache pamätiam a pamäťovým radičom.

Ak vám plocha cache pamätí stále nedáva zmysel (mne je to stále trochu záhadou :smile:),
pokúsim sa to vysvetliť. Cache pamäte sa síce zdajú byť veľké, no stále majú obmedzenú kapacitu.
V porovnaní s kapacitou DRAM čipu (niekoľko gigabajtov) sú malé (napríklad L3 cache má len niekoľko MB).
Práve menšia veľkosť je kľúčom k dosiahnutiu vyššej priepustnosti a nižšej latencie, no prináša aj svoje výzvy.

## Výzva

Nie je možné zmestiť celú DRAM do cache pamäte :smile:. Cache si preto musí vybrať podmnožinu pamäte,
ktorú bude uchovávať, a musí byť pri tomto výbere dostatočne inteligentná. Cache pamäte využívajú niečo,
čo sa nazýva lokalita dát. V skratke to znamená, že dáta, ktoré boli použité, budú pravdepodobne použité znova.
Existujú však rôzne typy dátovej lokality.

### Priestorová lokalita

Predstavte si, že iterujete cez pole celých čísel a inkrementujete každý jeho prvok.

```c
for (int i = 0; i < ARRAY_SIZE; i++) {
    array[i]++;
}
```
V tomto cykle môže cache využiť priestorovú lokalitu (*spatial locality*), pretože ďalšia adresa,
ku ktorej program pristúpi, sa nachádza blízko predchádzajúcej adresy. Pri prvom prístupe k poľu
sa do jednej cache line načíta viacero prvkov, čo znamená, že nie je potrebné vykonávať toľko
read/write požiadaviek do DRAM. Toto sa nazýva *sekvenčný prístupový vzor* (*sequential access pattern*).
Dátové štruktúry, ktoré sekvenčný prístup nevyužívajú, sú typicky hash tabuľky. Tie používajú
*náhodný prístupový vzor* (*random access pattern*). Pri využívaní priestorovej lokality
sa bottleneckom stáva veľkosť cache line.

### Časová lokalita

Časová lokalita (*temporal locality*) je tendencia programov opakovane používať tie isté dáta počas
svojho vykonávania. V našom príklade s cyklom by sme mohli povedať, že premenná `i` vykazuje časovú
lokalitu, pretože sa inkrementuje na konci každej iterácie cyklu (ignorujúc fakt, že je uložená
v registri procesoru). Jediným obmedzujúcim faktorom je v tomto prípade veľkosť cache.

Existujú aj ďalšie typy lokality, ktoré sú odvodené od týchto dvoch základných. Cache pamäte určujú
pracovnú podmnožinu pamäte na základe dátovej lokality pomocou politík správy cache (*cache replacement policies*).
Týmto politikám sa budem venovať v ďalšom článku.

## Čo je cache?

Podľa môjho názoru možno za cache označiť čokoľvek, čo dokáže:
- znížiť počet read/write požiadaviek, a tým znížiť požadovanú priepustnosť pamäťového systému,
- znížiť latenciu read/write požiadaviek.

Keďže ide o FPGA blog, budem cache označovať ako komponenty pamäťového systému implementované
vo FPGA logike, ktoré vykonávajú vyššie spomenuté úlohy.

### Plne asociatívna cache

{{<
    dynamic-image
    light="img/fully-assoc-light.svg"
    dark="img/fully-assoc-dark.svg"
    alt="Plne asociatívna cache"
>}}

Obrázok vyššie zobrazuje plne asociatívnu cache (*fully associative cache*) s kapacitou 4 prvkov.
Ide o najjednoduchší typ cache z pohľadu návrhu, no zároveň spotrebúva veľké množstvo plochy čipu,
pretože pre každý prvok uložený v cache musí existovať samostatný komparátor adries.
Keď sa jadro pokúsi prečítať určitú adresu, táto adresa sa porovnáva so všetkými adresami uloženými
v cache. Ak sa nájde zhoda, vrátia sa príslušné dáta. Toto sa nazýva **cache hit** a dáta sú dostupné
takmer okamžite.
Plne asociatívna cache má najlepšie vlastnosti z pohľadu kolízií - ku kolíziám v podstate nedochádza,
môžeme jednoducho len naraziť na nedostatok miesta. Toto riešenie však neškáluje príliš dobre:
- adresové komparátory zaberajú veľkú plochu čipu,
- vzniká rozsiahla kombinačná cesta, čo vedie k nízkej pracovnej frekvencii.

### Priamo mapovaná cache (direct mapped cache)

A sme pri ďalšom jednoduchom a zdanlivo očividnom riešení. Kľúč (adresu) preženieme cez hashovaciu funkciu,
výsledný hash použijeme ako adresu do block RAM, načítame dáta a porovnáme kľúč - podľa toho zistíme,
či sa dáta nachádzajú v cache alebo nie.
Tento variant škáluje prakticky rovnako dobre ako samotné block RAM pamäte. Má však jeden menší háčik - 
hashovacia funkcia môže zaviesť príliš veľkú mieru náhodnosti:
1. programátor nedokáže jednoducho odhadnúť využitie cache,
2. pre porovnanie je potrebné ukladať celú adresu.

Poďme toto riešenie trochu vylepšiť. Chceme navrhnúť cache s kapacitou 512 prvkov - na adresovanie
v rámci block RAM potrebujeme 9 bitov. Celková adresa má 32 bitov. Adresu preto rozdelíme na dve časti:
- **tag** (23 najvýznamnejších bitov),
- **index** (9 najmenej významných bitov).

Index sa používa na adresovanie dát v cache. Tag slúži na overenie, že dáta uložené v cache
sú skutočne tie, ktoré hľadáme - funguje teda ako náš kľúč. Programátor teraz dokáže predvídať, aké dáta
budú uložené v cache, a zároveň sme ušetrili 29 % plochy block RAM.

Pamätáte si na priestorovú lokalitu (*spatial locality*)? V tomto variante ju nedokážeme využiť,
pretože v jednej cache line ukladáme iba jeden bajt dát. Preto do návrhu pridáme ďalší trik.
Chceme do jednej cache line uložiť 64 B dát (čo zodpovedá 16 integerom), takže adresu rozdelíme
na tri časti:
- **tag** (17 najvýznamnejších bitov),
- **index** (9 bitov),
- **offset** (6 najmenej významných bitov).

{{<
    dynamic-image
    light="img/direct-mapped-light.svg"
    dark="img/direct-mapped-dark.svg"
    alt="Priamo mapovaná cache"
>}}

Týmto spôsobom sa pri iterovaní poľa ukladajú do cache aj dátové prvky, ku ktorým program
pristúpi neskôr. Získali sme tak škálovateľnú cache, no pravdepodobnosť kolízií je pomerne vysoká.
Keď dôjde ku kolízii alebo nastane **cache miss**, cache musí vyradiť aktuálnu cache line
a nahradiť ju novou. Vyraďovanie cache line prináša dodatočnú latenciu.
Ďalším problémom je, že cache si nedokáže vyberať, ktoré dáta bude uchovávať. Práve preto naši
šikovní kolegovia vyvinuli **set asociatívnu cache** (*set associative cache*).

### Set asociatívna cache

{{<
    dynamic-image
    light="img/set-assoc-light.svg"
    dark="img/set-assoc-dark.svg"
    alt="Set asociatívna cache"
>}}

Set asociatívnu cache si môžeme predstaviť ako plne asociatívnu cache
vnútri priamo mapovanej cache :smile:. Princíp rozdelenia adresy zostáva rovnaký. Rozdiel je však v tom,
že na každom indexe sa nenachádza iba jedna cache line, ale viacero.
Cache si tak pri vzniku cache miss dokáže vybrať, ktorú cache line vyradí. Najvhodnejšiu cache line
na vyradenie určuje **politika nahrádzania cache** (*cache replacement policy*).
Počet cache lines priradených jednému indexu sa nazýva **asociativita cache** (*cache associativity*).

Toto riešenie poskytuje možnosť škálovať cache podľa potreby. Ak potrebujete dosiahnuť vyššiu pracovnú
frekvenciu, môžete znížiť asociativitu cache. Ak naopak vaše časovanie vyzerá až príliš dobre,
môžete z cache vyťažiť maximum zvýšením asociativity. Nebojte sa experimentovať, práve v tom spočíva krása FPGA.

## Zhrnutie

Na konci dňa sú cache pamäte šikovným spôsobom, ako obísť limity pamäťových systémov. Možno nevyriešia
každý problém, no vo väčšine prípadov odvádzajú skvelú prácu pri zrýchľovaní systému. Od jednoduchých
plne asociatívnych cache až po pokročilejšie set asociatívne varianty prešli dlhú cestu v snahe
vyťažiť maximum z dostupných zdrojov.

Samozrejme, nejde o žiadnu mágiu. Kolízie, obmedzená kapacita či občasná penalizácia pri vyraďovaní dát
sú jednoducho súčasťou hry. Vo FPGA návrhoch však predstavujú priestor na tvorbu vlastných riešení
prispôsobených konkrétnym požiadavkám. Ako prirodzené pokračovanie sa v ďalšom článku pozrieme na jednu
z najzaujímavejších a najviac skúmaných tém v oblasti cache - **politiky správy cache**
(*cache replacement policies*).

Aj keď cache nie sú univerzálnym riešením pamäťových bottleneckov, predstavujú nevyhnutný nástroj
v snahe dosiahnuť vyšší výkon a efektivitu moderných výpočtových systémov. Pochopenie a optimalizácia
ich návrhu sú kľúčom k odomknutiu plného potenciálu dnešných systémov - a možno, v duchu poznámky
môjho profesora, sa vždy nájde miesto ešte pre jednu cache :grin:.
