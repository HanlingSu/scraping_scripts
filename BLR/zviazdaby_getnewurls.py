# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
import time
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
import re
import pandas as pd



# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

text = """
https://zviazda.by/ru/news/20241211/1733918279-politiki-i-politikany-poslesloviya-kovida-kto-pridumal-epidemiyu-i-kto
https://zviazda.by/ru/news/20241211/1733911670-lukashenko-podpisal-zakon-kotorym-kompleksno-korrektiruetsya-kodeks-ob
https://zviazda.by/ru/news/20241211/1733912751-ocherednaya-batareya-sovremennyh-zenitnyh-raketnyh-kompleksov-tor-m2
https://zviazda.by/ru/news/20241211/1733912471-mvd-ustanovleny-imena-desyati-ekstremistov
https://zviazda.by/ru/news/20241211/1733912304-v-kitae-na-zheleznoy-doroge-perevezeno-svyshe-4-milliardov-chelovek
https://zviazda.by/ru/news/20241211/1733911545-v-kitae-opredelili-top-10-mediavyrazheniy
https://zviazda.by/ru/news/20241211/1733911244-predlagali-100-tys-evro-neudavshayasya-popytka-polskih-specsluzhb
https://zviazda.by/ru/news/20241211/1733911083-pensii-polnye-semeynyy-kapital-na-pogashenie-kredita
https://zviazda.by/ru/news/20241211/1733910802-edinstvo-izmereniy-i-ukreplenie-vneshnih-svyazey
https://zviazda.by/ru/news/20241211/1733910316-v-minske-ezhenedelno-vypolnyaetsya-okolo-100-operaciy-po
https://zviazda.by/ru/news/20241211/1733910001-shulgan-o-tarifah-rouminga-v-sg
https://zviazda.by/ru/news/20241211/1733909316-belorusy-zavoevali-shest-medaley-na-kubke-voronina-po-sportivnoy-gimnastike
https://zviazda.by/ru/news/20241211/1733909222-percov-rasskazal-o-znachimosti-molodyh-analitikov
https://zviazda.by/ru/news/20241211/1733909095-shkanova-vyigrala-vtoroe-serebro-v-slalome-na-kubke-rossii-v-polyarnyh
https://zviazda.by/ru/news/20241211/1733909005-v-nok-belarusi-podveli-itogi-uhodyashchego-goda
https://zviazda.by/ru/news/20241211/1733908349-hodba-protiv-bolyachek
https://zviazda.by/ru/news/20241210/1733822486-spros-beshenyy-lukashenko-poruchil-podderzhivat-i-prodvigat-takie
https://zviazda.by/ru/news/20241211/1733906412-lukashenko-v-raketnom-komplekse-oreshnik-vsya-puskovaya-ustanovka
https://zviazda.by/ru/news/20241211/1733904904-kazhdaya-problema-na-kontrole
https://zviazda.by/ru/news/20241211/1733903513-napolnyat-iskusstvom-dushu-libo-gde-nayti-orientiry-tvorchestva-i
https://zviazda.by/ru/news/20241211/1733898662-nashe-samoe-luchshee
https://zviazda.by/ru/news/20241210/1733825060-belarus-okazalas-na-tretem-meste-v-reytinge-stran-evropy-po-prognoziruemomu
https://zviazda.by/ru/news/20241210/1733824960-chleny-soveta-respubliki-provodyat-edinyy-den-priema-grazhdan-v-kazhdom
https://zviazda.by/ru/news/20241210/1733824824-v-mart-opredelili-perechen-sushchestvenno-vazhnyh-dlya-vnutrennego-rynka
https://zviazda.by/ru/news/20241210/1733824589-den-prav-cheloveka
https://zviazda.by/ru/news/20241210/1733824325-v-provincii-anhoy-proizvodstvo-kleykogo-risa-stalo-mnogomilliardnoy
https://zviazda.by/ru/news/20241210/1733822874-pogoda-na-vyhodnye-udaryat-morozy-do-minus-12
https://zviazda.by/ru/news/20241210/1733822694-belarus-v-lyubyh-ostryh-situaciyah-prizyvaet-k-miru-nasha-poziciya
https://zviazda.by/ru/news/20241209/1733735186-lukashenko-predlagaet-nizhegorodskoy-oblasti-novye-proekty-i-rasschityvaet
https://zviazda.by/ru/news/20241210/1733822062-edinstvo-delaet-nas-silnee
https://zviazda.by/ru/news/20241210/1733820245-prognoz-nauchno-tehnicheskogo-progressa-belarusi-na-blizhayshie-20-let
https://zviazda.by/ru/news/20241209/1733748383-mts-priznan-luchshim-mobilnym-operatorom-belarusi
https://zviazda.by/ru/news/20241210/1733819545-fantasticheskoe-shou-proshlo-v-minsk-arene
https://zviazda.by/be/news/20180423/1524497100-litaratura-dlya-dzyacey
https://zviazda.by/ru/nashe-schaste-zhit-odnoy-sudboyu-istorii-o-bratyah-grimm-moiseeva-t-matveenko-12
https://zviazda.by/ru/skazki-dlya-vesnushki-tayna-chernoy-statui-gushinec-p-12
https://zviazda.by/ru/news/20241209/1733741749-zakonoproekt-po-voprosam-ugolovnoy-otvetstvennosti-obsudili-na-ekspertnom
https://zviazda.by/ru/news/20241209/1733741528-sergeenko-belarus-vystupaet-za-postroenie-ravnoy-nedelimoy-evraziyskoy
https://zviazda.by/ru/news/20241209/1733725864-golovchenko-analogov-soyuznomu-gosudarstvu-v-mirovoy-praktike-net
https://zviazda.by/ru/news/20241209/1733735378-igor-sergeenko-provedet-lichnyy-priem-grazhdan-v-minske
https://zviazda.by/ru/news/20241209/1733735068-zakonoproekt-ob-obespechenii-edinstva-izmereniy-rassmotryat-deputaty-10
https://zviazda.by/ru/news/20241209/1733726406-golovchenko-rasskazal-o-chem-prezidenty-i-premery-belarusi-i-rossii
https://zviazda.by/ru/news/20241205/1733397184-lukashenko-v-soyuznom-gosudarstve-uzhe-sdelano-nemalo-no-neobhodimo-smelee
https://zviazda.by/ru/news/20241209/1733725712-mezencev-pro-obedinennyy-rynok-elektroenergii-sg
https://zviazda.by/ru/news/20241209/1733725339-belorusskiy-thekvondist-gurciev-vzyal-serebro-prestizhnogo-turnira-v-kitae
https://zviazda.by/ru/news/20241209/1733725207-mezencev-belarus-i-rossiya-sformirovali-edinuyu-oboronnuyu-politiku
https://zviazda.by/ru/news/20241206/1733463924-kakie-mery-prinimayutsya-chtoby-povysit-prestizh-selskohozyaystvennyh
https://zviazda.by/ru/news/20241205/1733381475-kak-klimaticheskie-anomalii-skazyvayutsya-na-pogodnyh-usloviyah-v-belarusi
https://zviazda.by/ru/news/20241207/1733578043-yunesko-vklyuchila-prazdnik-vesny-v-spisok-nematerialnogo-kulturnogo
https://zviazda.by/ru/news/20241207/1733579156-haki-glavnyy-cvet-sezona-kotoryy-segodnya-zavoeval-podiumy
https://zviazda.by/ru/news/20241207/1733575211-glavnye-muzhskie-manipulyacii-kotorye-dolzhna-znat-kazhdaya-zhenshchina
https://zviazda.by/ru/news/20241207/1733573644-derevnya-sychzhou-stala-populyarnym-turisticheskim-napravleniem
https://zviazda.by/ru/news/20241207/1733573314-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20241207/1733572528-v-cindao-prohodit-vystavka-poyas-i-put-obshchaya-krasota
https://zviazda.by/ru/news/20241207/1733566680-golovchenko-memorial-v-krasnom-berege-moshchnyy-zaslon-bezdushnym-popytkam
https://zviazda.by/ru/news/20241207/1733566139-marafon-edinstva-v-orshe-den-vtoroy
https://zviazda.by/ru/news/20241207/1733565980-rasskazyvaem-o-masshtabah-shou-vremya-nashih-pobed
https://zviazda.by/ru/news/20241207/1733565587-translyaciya-koncerta-vremya-vybralo-nas-v-orshe-budet-organizovana-na
https://zviazda.by/ru/news/20241207/1733565272-sergeenko-primet-uchastie-v-sovmestnom-zasedanii-soveta-pa-odkb-v-moskve
https://zviazda.by/ru/news/20241207/1733565148-v-yunnani-nachalas-kofeynaya-zhatva
https://zviazda.by/ru/news/20241207/1733564719-kak-programmnyy-kompleks-odno-okno-uprostil-kommunikaciyu-gosorganov-i
https://zviazda.by/ru/news/20241207/1733564398-vybor-budushchego-strany
https://zviazda.by/ru/news/20241207/1733563594-yarkoe-sportivnoe-shou-vremya-nashih-pobed-proydet-7-dekabrya-v-minske
https://zviazda.by/ru/news/20241207/1733560143-belarus-i-rossiya-zaklyuchili-dogovor-o-formirovanii-obedinennogo-rynka
https://zviazda.by/ru/news/20241207/1733559938-karpenko-na-prieme-grazhdan-v-gomele-professionalam-nuzhno-doveryat
https://zviazda.by/ru/news/20241207/1733559600-vkusnyatina-na-prazdnichnom-stole
https://zviazda.by/ru/news/20241205/1733387010-kak-obuchayut-traktoristov-mashinistov-v-vileyskom-gosudarstvennom
https://zviazda.by/ru/news/20241204/1733303889-prodavcy-kvartir-soglashayutsya-na-skidki
https://zviazda.by/ru/news/20241206/1733475693-zachem-krupnym-kompaniyam-ustoychivye-socialnye-iniciativy
https://zviazda.by/ru/news/20241206/1733476839-profsoyuzy-monitoryat-temperaturnyy-rezhim-na-rabochih-mestah
https://zviazda.by/ru/news/20241206/1733476547-chto-izmenitsya-v-zakone-po-voprosam-registracii-nedvizhimogo-imushchestva
https://zviazda.by/ru/news/20241206/1733471343-ivan-kubrakov-provel-vstrechu-s-nachalnikom-policii-dubaya
https://zviazda.by/ru/news/20241206/1733471138-moroz-o-marafone-edinstva-v-orshe
https://zviazda.by/ru/news/20241206/1733471003-v-chanchune-sobaki-roboty-rabotayut-na-gornolyzhnom-kurorte
https://zviazda.by/ru/news/20241206/1733470489-v-belarusi-zavershaetsya-sbor-podpisey-v-podderzhku-vydvizheniya-kandidatov
https://zviazda.by/ru/news/20241206/1733470238-kakoy-pogody-zhdat-v-eti-dni
https://zviazda.by/ru/news/20241206/1733469147-sudba-finalistov-faktarby-v-rukah-zriteley
https://zviazda.by/ru/news/20241206/1733468781-v-kirovske-veselo-proveli-prazdnik-kartofelya
https://zviazda.by/ru/news/20241205/1733397077-chto-na-povestke-dnya-v-sg-i-v-otnosheniyah-s-rossiey
https://zviazda.by/ru/news/20241205/1733392548-chleny-soveta-respubliki-provedut-edinyy-den-priema-grazhdan-v-kazhdom
https://zviazda.by/ru/news/20241205/1733392441-zakonoproekt-o-respublikanskom-byudzhete-na-2025-god-rassmotryat-deputaty
https://zviazda.by/ru/news/20241205/1733392337-lukashenko-odobril-proekt-dogovora-belarusi-i-rossii-o-garantiyah
https://zviazda.by/ru/news/20241205/1733392078-golovchenko-podhody-k-obespecheniyu-grazhdan-zhilem-nuzhdayutsya-v
https://zviazda.by/ru/news/20241205/1733391907-v-sinczyane-ispolzuyut-sputnikovye-chipy-i-bespilotniki-dlya-vypasa-skota
https://zviazda.by/ru/news/20241204/1733315877-petrishenko-o-priemah-grazhdan
https://zviazda.by/ru/news/20241205/1733391637-horoshaya-razrabotka-dolzhna-ne-lezhat-vnedryatsya-v-praktiku-i-rabotat
https://zviazda.by/ru/news/20241205/1733391214-svet-ishchushchiy-dobro
https://zviazda.by/ru/news/20241205/1733390764-profsoyuz-zhkh-podvel-itogi-raboty-za-pyatiletku
https://zviazda.by/ru/news/20241205/1733387803-kak-pomoch-sazhencam-perezimovat
https://zviazda.by/ru/news/20241205/1733385718-chto-yavlyaetsya-yakorem-dlya-mira-v-tayvanskom-prolive
https://zviazda.by/ru/news/20241205/1733382198-svetlana-agarval-muzyka-eto-moya-dusha
https://zviazda.by/ru/news/20241205/1733380969-brestchina-otmetila-yubiley
https://zviazda.by/ru/edition
https://zviazda.by/ru/news/20241204/1733315727-kak-cik-rabotaet-nad-povysheniem-pravovoy-kultury-grazhdan
https://zviazda.by/ru/news/20241204/1733315451-delegaciya-mvd-belarusi-prinimaet-uchastie-v-rabote-vsemirnogo-sammita
https://zviazda.by/ru/news/20241204/1733315253-v-silah-li-belarus-i-rossiya-narastit-tovarooborot-do-100-mlrd
https://zviazda.by/ru/news/20241204/1733315044-petkevich-predstavila-oblispolkomu-novogo-pomoshchnika-prezidenta
https://zviazda.by/ru/news/20241204/1733314918-v-processe-sbora-podpisey-zhalob-v-cik-ne-postupalo
https://zviazda.by/ru/news/20241204/1733314765-pochemu-vazhno-vovremya-vyyavit-vich-infekciyu
https://zviazda.by/ru/news/20241204/1733314445-zakonoproekt-po-voprosam-ispolnitelnogo-proizvodstva-prinyat-v-pervom
https://zviazda.by/ru/news/20241204/1733314311-zavtra-mozhno-obratitsya-v-profsoyuznye-obshchestvennye-priemnye
https://zviazda.by/ru/news/20241204/1733313944-chto-ne-tak-v-nauchnoy-sfere-belarusi-i-kak-eto-predlagayut-ispravit
https://zviazda.by/ru/news/20241204/1733313042-budut-li-v-regionah-belarusi-sozdavatsya-edinye-sluzhby-odno-okno
https://zviazda.by/ru/news/20241204/1733312796-derevya-v-pekine-uteplilis-uyutnymi-sviterami
https://zviazda.by/ru/news/20241204/1733312647-kgb-raskryl-podrobnosti-del-v-otnoshenii-belorusa-i-polyaka-kotorye
https://zviazda.by/ru/news/20241204/1733308597-mts-obespechil-nadezhnuyu-svyaz-v-nacionalnom-basseyne
https://zviazda.by/ru/news/20241204/1733309531-nashi-prava-nelzya-narushat-beznakazanno
https://zviazda.by/ru/news/20241204/1733309255-lukashenko-vo-mnogom-blagodarya-usiliyam-cik-vybory-v-belarusi-stali
https://zviazda.by/ru/about
https://zviazda.by/ru/news/20241203/1733215690-kak-lyudi-s-invalidnostyu-menyayut-mir-k-luchshemu
https://zviazda.by/ru/news/20241203/1733220851-predsedatel-kgk-belarusi-obratil-vnimanie-na-otsutstvie-edinoy-strategii
https://zviazda.by/ru/news/20241203/1733220681-respublikanskiy-patrioticheskiy-centr-v-brestskoy-kreposti-nachnet-rabotat
https://zviazda.by/ru/news/20241203/1733220554-v-kitae-vozrosla-populyarnost-rybalki
https://zviazda.by/en/news/20241203/1733219509-what-was-revolutionary-path-tsarist-general
https://zviazda.by/en/news/20241203/1733218717-karatkevich-was-published-azerbaijan
https://zviazda.by/ru/news/20241203/1733220247-aleksandr-bulak-vkladyvaya-v-nastoyashchee-sozdaem-budushchee
https://zviazda.by/en/news/20241203/1733217717-how-did-teflon-spread-around-world-and-cookware-non-stick-coating-really
https://zviazda.by/en/news/20241203/1733214199-belarusian-literature-world
https://zviazda.by/en/news/20241112/1731399019-what-pleased-visitors-bti-2024-exhibition
https://zviazda.by/en/news/20241203/1733210299-ke-la-si-guo-jia-wen-xue-ji-nian-bo-wu-guan-ju-ban-liao-bai-luo-si-wen-xue
https://zviazda.by/en/news/20241030/1730290713-olga-shpilevskaya-belarusian-women-really-carry-our-country
https://zviazda.by/en/news/20241112/1731397357-arthaos-gallery-has-opened-exhibition-two-young-belarusian-artists-once
https://zviazda.by/en/news/20241112/1731401736-what-do-bloggers-and-media-have-common
https://zviazda.by/en/news/20241203/1733208906-who-took-grand-prix-anniversary-listapad
https://zviazda.by/ru/news/20241203/1733219960-pogoda-dekabr-startuet-anomalnym-teplom
https://zviazda.by/ru/news/20241203/1733219367-brestskuyu-oblastnuyu-biblioteku-imeni-m-gorkogo-torzhestvenno-otkryli
https://zviazda.by/ru/news/20241203/1733219032-85-let-brestskoy-oblasti
https://zviazda.by/ru/news/20241203/1733218799-golovchenko-rasskazal-chto-belorusy-pokupayut-v-kredit-na-rodnyya-tavary
https://zviazda.by/ru/news/20241203/1733218678-v-sinczyane-sdan-v-ekspluataciyu-novyy-aeroport
https://zviazda.by/ru/news/20241203/1733217508-lukashenko-ukazal-na-kolossalnuyu-nedorabotku-pravitelstva-v-soprovozhdenii
https://zviazda.by/ru/news/20241203/1733217013-kak-proshel-marafon-edinstva-v-vitebske
https://zviazda.by/ru/news/20241102/1730533899-kak-teflon-zahvatil-ves-mir-i-chem-opasen
https://zviazda.by/en/news/20241112/1731399868-katerina-khadasevich-lisovaya-i-feel-happy-meet-readers
https://zviazda.by/ru/news/20241202/1733148415-mts-tv-sozdal-prazdnichnyy-advent-kalendar-s-kinopodarkami
https://zviazda.by/be/news/20160419/1461081953-gistoryya-i-krayaznaustva
https://zviazda.by/ru/news/20180423/1524474811-proza-0
https://zviazda.by/ru/rashenni-prymae-ck-z-arhiunyh-dakumentau-karlyukevich-selyameneu-v-16
https://zviazda.by/ru/botan-povest-karnauhova-i-12
https://zviazda.by/ru/volchonok-i-ego-druzya-skazka-nikolaev-d-6
https://zviazda.by/ru/news/20241127/1732698165-pravosudie-ili-politicheskaya-igra-resheniya-mus-i-ih-nichtozhnost
https://zviazda.by/ru/news/20241202/1733134542-lukashenko-poruchil-opredelitsya-s-budushchim-belorusskoy-neftyanoy
https://zviazda.by/ru/news/20241202/1733134416-belarus-i-rossiya-predstavili-svoe-videnie-evraziyskoy-hartii-mnogoobraziya
https://zviazda.by/ru/news/20241202/1733134304-v-kitae-stimuliruyut-razvitie-ekonomiki-lda-i-snega
https://zviazda.by/ru/news/20241202/1733134105-v-kakih-sferah-mogut-nayti-vzaimnyy-interes-belarus-i-pakistan
https://zviazda.by/ru/news/20241202/1733133994-golovchenko-rasskazal-kak-ekonomika-belarusi-udvoilas-za-20-let
https://zviazda.by/ru/news/20241202/1733131015-ruslan-cherneckiy-naznachen-ministrom-kultury-belarusi
https://zviazda.by/ru/news/20241202/1733130920-kochanova-ot-ustoychivogo-regionalnogo-razvitiya-zavisit-blagopoluchie
https://zviazda.by/ru/news/20241202/1733126100-trudovye-budni-mayora-milicii-makarevicha
https://zviazda.by/ru/news/20241130/1732962882-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20241129/1732830318-skolko-v-etom-godu-pridetsya-potratit-na-zimnie-prazdniki
https://zviazda.by/ru/news/20241130/1732964793-v-guanchzhou-prohodit-vystavka-kotoraya-posvyashchena-marko-polo
https://zviazda.by/ru/news/20241130/1732965991-toksichnye-otnosheniya-i-ih-posledstviya
https://zviazda.by/ru/news/20241130/1732964431-glavnyy-aksessuar-zimy-perchatki
https://zviazda.by/ru/news/20241201/1733035080-nikolay-lukashenko-ya-ego-absolyutnaya-kopiya
https://zviazda.by/ru/news/20241129/1732888098-delo-zhizni-arkadiya-shklyara
https://zviazda.by/ru/news/20241130/1732960860-kitayskiy-superkompyuter-tyanhe-vozglavil-mirovoy-reyting
https://zviazda.by/ru/news/20241130/1732959331-marafon-edinstva-v-vitebske-den-vtoroy
https://zviazda.by/ru/news/20241130/1732958541-zhurnalisty-tozhe-nesut-sereznuyu-otvetstvennost-za-sudbu-gosudarstva
https://zviazda.by/ru/news/20241130/1732954247-v-minske-otkrylas-vystavka-prodazha-tvoreniya-serdec
https://zviazda.by/ru/news/20241130/1732953815-aktualizirovan-sostav-predstaviteley-belarusi-v-komissii-po-pravam
https://zviazda.by/ru/news/20241130/1732953710-do-1-dekabrya-vse-transportnye-sredstva-dolzhny-pereobutsya
https://zviazda.by/ru/news/20241127/1732692595-usilena-zashchita-poluchateley-kreditov
https://zviazda.by/ru/news/20241128/1732778095-tatyana-ulasen-kogda-lyubish-i-semyu-i-teatr-nahodyatsya-kompromissy
https://zviazda.by/ru/news/20241128/1732784301-v-belarusi-vozrozhdayut-mestnuyu-porodu-krasnyh-korov
https://zviazda.by/ru/news/20241129/1732877849-lukashenko-mnogopolyarnost-eto-istoricheskaya-neizbezhnost
https://zviazda.by/ru/news/20241129/1732870405-marafon-edinstva-priehal-v-vitebsk
https://zviazda.by/ru/news/20241129/1732877646-golovchenko-proizvodstvo-indeyki-s-2021-goda-vyroslo-bolee-chem-v-tri-raza
https://zviazda.by/ru/news/20241128/1732777624-lukashenko-pribyl-s-rabochim-vizitom-v-kazahstan-na-sammit-odkb
https://zviazda.by/ru/news/20241128/1732787326-v-pustyne-gobi-zapushchena-masshtabnaya-fotoelektrostanciya
https://zviazda.by/ru/news/20241129/1732869881-kak-zakrytie-polskih-punktov-propuska-povliyalo-na-puteshestvennikov
https://zviazda.by/ru/news/20241129/1732831271-kakoy-pogody-zhdat-v-nachale-dekabrya
https://zviazda.by/ru/news/20241129/1732830895-v-bgu-otkroyut-dve-novye-specialnosti
https://zviazda.by/ru/news/20241129/1732831692-mogilevchanin-spas-sosedku-pri-pozhare
https://zviazda.by/ru/news/20241129/1732829179-kibermoshenniki-pridumyvayut-sezonnye-shemy-obmana
https://zviazda.by/ru/news/20241129/1732831458-mid-nravstvennost-i-chelovechnost-dolzhny-byt-v-osnove-lyubyh-resheniy-v
https://zviazda.by/ru/news/20241129/1732830624-kitayskie-vlasti-boryutsya-s-algoritmicheskoy-ekspluataciey-rabotnikov
https://zviazda.by/ru/news/20241128/1732795568-mts-predostavil-korporativnym-klientam-vozmozhnost-polzovatsya-lineykoy
https://zviazda.by/ru/news/20241128/1732796234-golovchenko-vruchil-gosnagrady-predstavitelyam-razlichnyh-sfer
https://zviazda.by/ru/news/20241128/1732796032-sovmestnoe-zasedanie-ministrov-inostrannyh-del-oborony-i-sekretarey
https://zviazda.by/ru/news/20241128/1732795930-v-mid-otreagirovali-na-izbienie-belorusskogo-podrostka-v-polshe
https://zviazda.by/ru/news/20241128/1732795685-zachem-est-klyukvu
https://zviazda.by/ru/news/20241128/1732790030-belorusskie-iniciativy-vostrebovany-u-partnerov-po-odkb
https://zviazda.by/ru/news/20241128/1732787489-v-kitae-aktivno-razvivaetsya-zoobiznes
https://zviazda.by/ru/news/20241128/1732786453-zachem-lyudi-obrashchayutsya-k-deputatam
https://zviazda.by/ru/news/20241128/1732785365-petkevich-vopros-raboty-s-lyudmi-zadacha-nomer-1
https://zviazda.by/ru/news/20241128/1732785051-utverzhdeny-pravila-dlya-shkolnikov-i-ih-roditeley
https://zviazda.by/ru/news/20241128/1732784648-v-stolice-proshla-yarmarka-vakansiy
https://zviazda.by/ru/news/20241127/1732716199-mts-uluchshil-kachestvo-svyazi-4g-v-60-naselennyh-punktah-strany
https://zviazda.by/ru/news/20241127/1732700608-lukashenko-posetil-v-pakistane-gorodok-murri-i-vstretilsya-s-semey-sharif
https://zviazda.by/ru/news/20241127/1732700504-lukashenko-provel-vstrechu-s-komanduyushchim-armiey-pakistana
https://zviazda.by/ru/news/20241127/1732700369-hod-realizacii-iniciativy-odin-rayon-odin-proekt-dolzhen-byt-na-postoyannom
https://zviazda.by/ru/news/20241127/1732700135-vo-vnutrenney-mongolii-nachalsya-zimniy-peregon-verblyudov
https://zviazda.by/ru/news/20241127/1732699960-v-strane-realizovyvaetsya-proekt-palaty-predstaviteley-molodezh-dlya
https://zviazda.by/ru/news/20241127/1732699477-ryzhenkov-o-razvitii-otnosheniy-s-pakistanom-my-pod-nadezhnoy-kryshey
https://zviazda.by/ru/news/20241127/1732699215-iz-kitayskih-vuzov-vypustyatsya-svyshe-12-millionov-chelovek
https://zviazda.by/ru/news/20241127/1732698917-ot-chego-voznikaet-osteoporoz-i-kak-ego-predupredit
https://zviazda.by/ru/news/20241127/1732698432-lukashenko-i-sharif-vyskazalis-o-situacii-na-blizhnem-vostoke-i-v-ukraine
https://zviazda.by/ru/news/20241127/1732693603-kakie-zavedeniya-obshchestvennogo-pitaniya-otkryvayutsya-segodnya-v
https://zviazda.by/ru/news/20241127/1732692800-kto-v-otvete-za-prirodu
https://zviazda.by/ru/news/20241126/1732621521-repeticiya-centralizovannogo-ekzamena-proydet-v-fevrale-2025-goda
https://zviazda.by/ru/news/20241126/1732621285-programma-sotrudnichestva-s-rf-po-atomnym-neenergeticheskim-i-neatomnym
https://zviazda.by/ru/news/20241126/1732621154-kochanova-o-kachestve-nashih-produktov-znayut-daleko-za-predelami-strany
https://zviazda.by/ru/news/20241126/1732621015-marafon-edinstva-masshtabiruetsya
https://zviazda.by/ru/news/20241126/1732620836-kak-spasateli-minshchiny-predotvrashchayut-tragedii
https://zviazda.by/ru/news/20241126/1732619152-v-kitae-razvivayut-dobychu-lesnyh-resursov-dlya-proizvodstva-produktov
https://zviazda.by/ru/news/20241126/1732618960-pogoda-bystraya-zima-otmenyaetsya
https://zviazda.by/ru/news/20241126/1732618726-kakie-voprosy-podnimalis-na-mezhdunarodnoy-voenno-nauchnoy-konferencii
https://zviazda.by/ru/news/20241126/1732616941-kakuyu-rol-sygral-polockiy-cerkovnyy-sobor
https://zviazda.by/ru/news/20241126/1732613586-ryzhenkov-obsudil-s-pakistanskim-kollegoy-dvustoronnyuyu-povestku-i
https://zviazda.by/ru/news/20241126/1732613403-kitayskaya-ekonomika-prodolzhit-vosstanavlivatsya-i-uluchshatsya
https://zviazda.by/ru/news/20241126/1732612516-lukashenko-belarusi-i-pakistanu-neobhodimo-monetizirovat-vysokiy-uroven
https://zviazda.by/ru/news/20241126/1732612400-belarus-i-pakistan-podpisali-dorozhnuyu-kartu-po-razvitiyu-vsestoronnego
https://zviazda.by/ru/news/20241126/1732611798-novyy-format-enciklopedii
https://zviazda.by/ru/news/20241126/1732608758-prazdnik-so-znakom-kachestva
https://zviazda.by/ru/news/20241126/1732604976-kod-k-predkam-narodnaya-tradiciya-kak-brend-rechicy
https://zviazda.by/ru/news/20241125/1732540155-mts-obespechil-svyazyu-uchastnikov-marafona-edinstva
https://zviazda.by/ru/news/20241125/1732533360-sergeenko-provedet-29-noyabrya-lichnyy-priem-grazhdan-v-sharkovshchine
https://zviazda.by/ru/news/20241125/1732533218-beloruska-koroleva-vzyala-serebro-v-sprinte-na-etape-kubka-rossii-po
https://zviazda.by/ru/news/20241125/1732525209-gigin-ob-originalnom-formate-i-atmosfere-proektov-marafona-edinstva
https://zviazda.by/ru/news/20241125/1732524875-obem-proizvodstva-new-avto-v-kitae-vpervye-prevysil-10-millionov
https://zviazda.by/ru/news/20241122/1732259831-kakie-novye-vkusy-prezentovali-proizvoditeli-produktov-pitaniya-na
https://zviazda.by/ru/news/20241122/1732262505-kakie-produkty-pomogut-borotsya-s-golodom-i-holodom-bez-ushcherba-dlya
https://zviazda.by/ru/news/20241125/1732524679-belorusskaya-legkoatletka-nemogay-vyigrala-marafon-v-kitae
https://zviazda.by/ru/news/20241120/1732092631-prichina-kazhdogo-chetvertogo-pozhara-nepotushennye-sigarety
https://zviazda.by/ru/news/20241122/1732257754-kak-podgotovit-avtomobil-k-zime
https://zviazda.by/ru/news/20241123/1732357587-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20241125/1732524379-lukashenko-napravilsya-s-oficialnym-vizitom-v-pakistan
https://zviazda.by/ru/news/20241125/1732524202-s-kakimi-vyzovami-stalkivaetsya-odkb-i-kak-im-protivostoit-rasskazal-gensek
https://zviazda.by/ru/news/20241123/1732357990-v-provincii-heylunczyan-nashli-svyshe-90-tysyach-kamennyh-izdeliy-epohi
https://zviazda.by/ru/news/20241123/1732357861-minimalizm-90-h-vnevremennaya-elegantnost
https://zviazda.by/ru/news/20241123/1732377617-kak-zastavit-rebyonka-ubiratsya-v-komnate-prostye-sovety-dlya-roditeley
https://zviazda.by/ru/news/20241123/1732357404-sbor-gerbariya-nabiraet-populyarnost-sredi-kitayskoy-molodezhi
https://zviazda.by/ru/news/20241123/1732355038-kitayskie-uchenye-nashli-novyy-sposob-podslashchivaniya-pomidorov
https://zviazda.by/ru/news/20241123/1732358814-razrabotka-novoy-koncepcii-bezopasnosti-soyuznogo-gosudarstva-velas-vmeste
https://zviazda.by/ru/news/20241123/1732358691-nesmotrya-na-napryazhennuyu-situaciyu-u-granic-belarusi-v-strane
https://zviazda.by/ru/news/20241123/1732354662-obem-rynka-kitayskih-mikrodram-prevysit-50-milliardov-yuaney
https://zviazda.by/ru/news/20241123/1732354406-kak-nas-obmanyvayut-moshenniki
https://zviazda.by/ru/news/20241123/1732354097-lukashenko-podpisal-ukaz-o-prieme-v-grazhdanstvo-257-chelovek-iz-16
https://zviazda.by/ru/news/20241122/1732262969-chto-lukashenko-reshil-obsudit-so-studentami-gumanitariyami
https://zviazda.by/ru/news/20241123/1732349688-vtoroy-den-marafona-edinstva-prohodit-v-mogileve
https://zviazda.by/ru/news/20241121/1732170899-schaste-tam-gde-semya
https://zviazda.by/ru/news/20241120/1732093178-kak-zakrepit-molodye-kadry-v-derevne
https://zviazda.by/ru/news/20241121/1732169814-uroven-energeticheskoy-samostoyatelnosti-strany-sushchestvenno-povysilsya
https://zviazda.by/ru/news/20241122/1732274665-mts-tv-sobral-7-kinolent-s-hyu-grantom-na-kazhdyy-den
https://zviazda.by/ru/news/20241122/1732270723-agrarii-belarusi-podnyali-bolee-87-zyabi
https://zviazda.by/ru/news/20241122/1732270507-novshestva-v-usloviyah-oplaty-truda-byudzhetnikov-razyasnili-v-mintruda
https://zviazda.by/ru/news/20241122/1732270400-sergeenko-vazhno-obespechit-cifrovuyu-transformaciyu-realnogo-sektora
https://zviazda.by/ru/news/20241122/1732266848-v-kitae-nachalos-stroitelstvo-gruzovogo-kosmicheskogo-chelnoka-haalun
https://zviazda.by/ru/news/20241122/1732265285-sovet-mpa-sng-prinyal-obrashchenie-v-svyazi-s-80-y-godovshchinoy-pobedy-v
https://zviazda.by/ru/news/20241122/1732265146-v-gomele-s-1-dekabrya-poyavitsya-novyy-roditelskiy-marshrut
https://zviazda.by/ru/news/20241122/1732264508-pogoda-prizhdali-silnyy-sneg
https://zviazda.by/ru/news/20241122/1732263901-lukashenko-prinyal-s-dokladom-glavu-administracii-prezidenta
https://zviazda.by/ru/news/20241122/1732263519-profsoyuz-zapustil-proekt-put-nezavisimosti-dlya-molodezhi-sfery-zhkh
https://zviazda.by/ru/news/20241122/1732262199-7-kitayskih-dereven-nazvany-luchshimi-v-mire
https://zviazda.by/ru/news/20241122/1732260935-karanik-obshchiy-kulturnyy-fundament-pomogaet-belarusi-i-rossii-ruka-ob
https://zviazda.by/ru/news/20241121/1732195041-mts-provel-master-klassy-po-profilaktike-kiberbullinga-dlya-800
https://zviazda.by/ru/news/20241121/1732187009-golovchenko-podcherknul-vazhnost-razvitiya-sotrudnichestva-v-soyuznom
https://zviazda.by/ru/news/20241121/1732186558-kak-boeviki-iz-chisla-beglyh-planiruyut-vtorzhenie-v-belarus
https://zviazda.by/ru/news/20241121/1732186381-na-krupneyshey-ferme-kitaya-provoditsya-zelenaya-transformaciya
https://zviazda.by/ru/news/20241121/1732186232-igor-sergeenko-ochen-mnogo-zavisit-ot-molodyh-specialistov-kotorye-dolzhny
https://zviazda.by/ru/news/20241121/1732185858-kakie-zadachi-stoyat-pered-soyuznym-informacionnym-prostranstvom
https://zviazda.by/ru/news/20241121/1732185478-opredeleny-pobediteli-sredi-talantlivoy-molodezhi
https://zviazda.by/ru/news/20241121/1732184108-sostoyalsya-ocherednoy-etap-komandno-shtabnyh-ucheniy
https://zviazda.by/ru/news/20241121/1732183233-belorusskaya-molodezh-za-razvitie-zelenoy-ekonomiki
https://zviazda.by/ru/news/20241121/1732182895-dialog-dlya-budushchego
https://zviazda.by/ru/news/20241121/1732181163-proekt-s-imenem
https://zviazda.by/ru/news/20241121/1732180800-akcent-na-kachestvo-i-podderzhku
https://zviazda.by/ru/news/20241121/1732180471-lukashenko-problemy-kotorye-trevozhat-lyudey-dlya-menya-ochen-vazhny-chtoby
https://zviazda.by/ru/news/20241121/1732180363-rezhim-kontrterroristicheskoy-operacii-vveden-na-territorii-grodno-i
https://zviazda.by/ru/news/20241030/1730284374-ispytanie-nezavisimostyu
https://zviazda.by/ru/news/20241121/1732177539-nam-est-chem-otvetit-yadernyy-shchit-i-mech
https://zviazda.by/ru/news/20241120/1732105033-mts-predlozhil-smartfon-za-1-rubl
https://zviazda.by/ru/news/20241119/1732013074-lukashenko-provedet-zasedanie-prezidiuma-vsebelorusskogo-narodnogo
https://zviazda.by/ru/news/20241120/1732107279-golovchenko-situaciya-v-ekonomike-stabilnaya-povyshaetsya-uroven-zhizni
https://zviazda.by/ru/news/20241120/1732107112-v-guanchzhou-zafiksirovano-samoe-dlinnoe-leto
https://zviazda.by/ru/news/20241120/1732106899-obedinenie-usiliy-stran-odkb-pozvolyaet-podderzhivat-mir-na-evraziyskom
https://zviazda.by/ru/news/20241120/1732106743-territorialnymi-komissiyami-po-vyboram-prezidenta-akkreditovany-800
https://zviazda.by/ru/news/20241120/1732106515-vo-vtoroy-den-ucheniy-otrabotayutsya-deystviya-po-presecheniyu-gruppovyh
https://zviazda.by/ru/news/20241120/1732106243-platezhnye-sistemy-alipay-i-wechat-dostupny-dlya-derzhateley-zarubezhnyh
https://zviazda.by/ru/news/20241120/1732106013-vvp-plyusuet-s-uskorennymi-tempami
https://zviazda.by/ru/news/20241120/1732105654-v-strane-prohodyat-komandno-shtabnye-ucheniya-s-uchastiem-subektov
https://zviazda.by/ru/news/20241120/1732105263-zadacha-parlamentariev-videt-i-pomogat
https://zviazda.by/ru/news/20241120/1732104941-kubrakov-ot-svoevremennogo-obmena-informaciey-zavisit-operativnost
https://zviazda.by/ru/news/20241120/1732103968-kak-zashchitit-rebenka-ot-atopicheskogo-dermatita
https://zviazda.by/ru/news/20220707/1657191778-tatyana-demidovich-vdohnovenie-napolnyaet-menya-zhiznelyubiem
https://zviazda.by/ru/news/20241120/1732092087-programmu-kachestvennogo-pitaniya-razrabotali-v-grodnenskom-agrarnom
https://zviazda.by/ru/kotra-vershy-abrazki-rusilka-v-6
https://zviazda.by/ru/oshibka-razini-ili-bolshoe-puteshestvie-malenkih-chelovechkov-skazka-shestakov-m-6
https://zviazda.by/ru/prelyudiya-rahmaninova-ili-sovety-psa-po-klichke-relaks-povest-karnauhova-i-6
https://zviazda.by/ru/novogodnie-priklyucheniya-plyushika-i-li-li-mao-rong-rong-he-li-li-de-xin-nian-li-xian-ji-skazka
https://zviazda.by/ru/lyubina-sukenka-apavyadanne-drabysheuskaya-v-12
https://zviazda.by/ru/day-lapu-mesyac-prygodnickaya-apovesc-kazka-marcinovich-6
https://zviazda.by/ru/sonino-detstvo-rasskazy-gushinec-p-6
https://zviazda.by/ru/news/20241116/1731747619-prezident-pozdravil-rabotnikov-i-veteranov-selskogo-hozyaystva-i
https://zviazda.by/ru/news/20241119/1732004129-v-mogileve-prodolzhaetsya-registraciya-na-kvest-eto-vse-moe-rodnoe
https://zviazda.by/ru/news/20241119/1732003488-na-odnoy-volne-s-bobruyskom
https://zviazda.by/ru/news/20241119/1732001491-verhovnyy-sud-belarusi-nachinaet-rassmotrenie-dela-smovskogo-po-faktam
https://zviazda.by/ru/news/20241119/1732001296-produkciya-malyh-kitayskih-predpriyatiy-zavoevyvaet-mirovye-rynki
https://zviazda.by/ru/news/20241119/1731967140-lisheny-zvaniy-bolee-20-byvshih-voennosluzhashchih-i-sotrudnikov-silovyh
https://zviazda.by/ru/news/20241119/1731968358-za-kakimi-znaniyami-priezzhayut-belorusy-zarubezhya
https://zviazda.by/ru/news/20241119/1731966768-fpb-nagradila-luchshih-molodyh-profaktivistov-i-otlichnikov-ucheby
https://zviazda.by/ru/news/20241119/1731966511-pogoda-podmorozit-do-minus-7-gradusov
https://zviazda.by/ru/news/20241119/1732000060-mvd-provodit-komandno-shtabnye-ucheniya-na-territorii-belarusi
https://zviazda.by/ru/news/20241119/1731966179-molodezhnyy-parlament-sereznaya-shkola-dlya-professionalnogo-i
https://zviazda.by/ru/news/20241119/1731965498-v-kitae-vypustyat-pamyatnuyu-monetu-kotoraya-posvyashchena-pekinskoy-opere
https://zviazda.by/ru/news/20241118/1731920163-sovet-respubliki-odobril-zakonoproekt-o-byudzhete-fonda-soczashchity
https://zviazda.by/ru/news/20241118/1731919974-uborku-saharnoy-svekly-i-kukuruzy-na-zerno-zavershili-v-belarusi
https://zviazda.by/ru/news/20241118/1731919713-naskolko-vygodno-investirovat-v-regionalnye-iniciativy
https://zviazda.by/ru/news/20241118/1731919528-vice-premer-ocenil-agrosezon-2024
https://zviazda.by/ru/news/20241118/1731919233-krutoy-o-hode-elektoralnoy-kampanii-absolyutno-spokoynyy-process-nikakih
https://zviazda.by/ru/news/20241116/1731751456-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20241114/1731567084-s-kakimi-rezultatami-belorusskie-agrarii-vyhodyat-k-svoemu-prazdniku
https://zviazda.by/ru/news/20241114/1731567846-pochem-v-etom-godu-glavnyy-zimniy-produkt
https://zviazda.by/ru/news/20241116/1731751732-v-provincii-shansi-otkrylsya-muzey-taosy
https://zviazda.by/ru/news/20241116/1731751088-kak-vospitat-emocionalno-zdorovogo-rebyonka-sovety-psihologa
https://zviazda.by/ru/news/20241116/1731750358-v-guychzhou-otmechayut-novyy-god-narodnosti-myao
https://zviazda.by/ru/news/20241116/1731747197-pastelnye-ottenki-v-kollekciyah-sezona-osen-zima-20242025
https://zviazda.by/ru/news/20241116/1731758985-kompaniya-mts-prezentovala-unikalnyy-merch
https://zviazda.by/ru/news/20241116/1731746908-v-kitae-kolichestvo-prazdnichnyh-vyhodnyh-uvelicheno-na-dva-dnya
https://zviazda.by/ru/news/20241116/1731754548-lukashenko-nagradil-peredovikov-apk-mogilevskoy-oblasti
https://zviazda.by/ru/news/20241116/1731754312-kak-belorusy-budut-otdyhat-i-rabotat-v-2025-godu
https://zviazda.by/ru/news/20241116/1731746368-sovremennye-tehnologii-pomogayut-uvelichivat-vyzhivaemost-pacientov-pri
https://zviazda.by/ru/news/20241116/1731744013-snyatie-ogranicheniy-rabotayushchim-pensioneram-i-semeynyy-kapital
https://zviazda.by/ru/news/20241116/1731743838-v-provincii-fuczyan-k-elektroseti-podklyuchen-unikalnyy-fotoelektricheskiy
https://zviazda.by/ru/news/20241116/1731743235-dyshat-polnoy-grudyu-v-gorodah-pomozhet-razvitie-ekologicheskogo-transporta
https://zviazda.by/ru/news/20241113/1731491013-s-kakimi-problemami-chashche-vsego-obrashchayutsya-rabotniki-i-kakie-shansy
https://zviazda.by/ru/news/20241115/1731679016-mts-tv-sobral-yuzhnokoreyskie-trillery-kotorye-znayut-vo-vsem-mire
https://zviazda.by/ru/news/20241115/1731668698-kochanova-o-rabote-s-grazhdanami-na-lichnyh-priemah
https://zviazda.by/ru/news/20241115/1731668259-hrenin-provel-vyezdnoy-priem-grazhdan-v-zhodino
https://zviazda.by/ru/news/20241115/1731667564-belarus-gotova-iskat-puti-resheniya-problem-nelegalnoy-migracii-i
https://zviazda.by/ru/news/20241115/1731667375-vyezdnoe-zasedanie-prezidiuma-soveta-respubliki-prohodit-v-shumilino
https://zviazda.by/ru/news/20241115/1731667262-volfovich-belarus-demonstriruet-iniciativu-k-resheniyu-problemy-nelegalnoy
https://zviazda.by/ru/news/20241115/1731666991-vo-vnutrenney-mongolii-startoval-sezon-zimnego-turizma
https://zviazda.by/ru/news/20241115/1731665797-kochanova-zhenshchiny-ediny-v-ustremleniyah-sohranit-svoyu-suverennuyu
https://zviazda.by/ru/news/20241115/1731665492-belorusskaya-molodezh-vystupaet-za-razvitie-zelenoy-ekonomiki
https://zviazda.by/ru/news/20241115/1731665169-na-stranu-obrushitsya-mokryy-sneg
https://zviazda.by/ru/news/20241115/1731661907-belarus-i-kazahstan-podpisali-dokumenty-o-sotrudnichestve
https://zviazda.by/ru/news/20241115/1731661736-golovchenko-belarus-gotova-postavlyat-v-kazahstan-aminokisloty-i
https://zviazda.by/ru/news/20241115/1731657939-kak-dlya-specialistov-osvod-proshlo-samoe-zharkoe-leto
https://zviazda.by/ru/news/20241114/1731574023-lukashenko-oznakomitsya-s-obnovlennym-stolichnym-stadionom-traktor
https://zviazda.by/ru/news/20241115/1731654158-golovchenko-belarusi-i-kazahstanu-nuzhno-obespechit-polozhitelnuyu-dinamiku
https://zviazda.by/ru/news/20241114/1731581875-deputaty-prinyali-vo-vtorom-chtenii-zakonoproekt-po-voprosam-obrazovaniya
https://zviazda.by/ru/news/20241114/1731575924-socopros-absolyutnoe-bolshinstvo-belorusov-prinimayut-uchastie-v-vyborah
https://zviazda.by/ru/news/20241114/1731575721-v-provincii-anhoy-razvivayut-golubikovuyu-industriyu
https://zviazda.by/ru/news/20241114/1731575268-patrioticheskiy-forum-belpochty-zainteresoval-molodezh
https://zviazda.by/ru/news/20241114/1731574970-v-bgu-otkryli-ocherednoy-imennoy-kabinet
https://zviazda.by/ru/news/20241114/1731574311-sergeenko-pererabatyvayushchie-kombinaty-slucka-obedinyaet-nacelennost-na
https://zviazda.by/ru/news/20241114/1731573868-sergeenko-vse-popytki-izolirovat-belarus-na-mirovoy-arene-terpyat-neudachu
https://zviazda.by/ru/news/20241114/1731567589-ne-razbezhalis-vo-vremya-remonta-zhit-vam-vsegda-vmeste
https://zviazda.by/ru/news/20241113/1731499005-nauchisvoihblizkih-mts-otkryvaet-novyy-nabor-v-besplatnuyu-onlayn-shkolu
https://zviazda.by/ru/news/20241113/1731497073-v-belarusi-otkryto-okolo-142-tys-depozitnyh-schetov-po-programme-semeynyy
https://zviazda.by/ru/news/20241113/1731496942-my-yavlyaemsya-svidetelyami-i-uchastnikami-globalnyh-geopoliticheskih
https://zviazda.by/ru/news/20241113/1731496796-gimnaziya-no-1-slucka-obrazec-dlya-vsey-sistemy-obshchego-srednego
https://zviazda.by/ru/news/20241113/1731496641-na-kakih-usloviyah-prohodit-zaselenie-v-socialnye-pansionaty
https://zviazda.by/ru/news/20241113/1731496448-kakaya-vakcina-sposobna-zashchitit-ot-grippa
https://zviazda.by/ru/news/20241113/1731496289-shenchzhen-priznan-luchshim-umnym-gorodom-mira
https://zviazda.by/ru/news/20241113/1731496136-sergey-bobrikov-prekrashchaet-svoe-uchastie-v-izbiratelnoy-kampanii
https://zviazda.by/ru/news/20241113/1731495812-v-belarusi-s-uchetom-rapsa-namolotili-103-mln-tonn-zerna
https://zviazda.by/ru/news/20241113/1731495698-v-bobruyske-priglashayut-komandy-dlya-uchastiya-v-kveste-eto-vse-moe-rodnoe
https://zviazda.by/ru/news/20241113/1731495042-kollektivnyy-dogovor-v-ukazannye-sroki
https://zviazda.by/ru/news/20241113/1731493931-povysitsya-socialnaya-zashchishchennost-veteranov-i-postradavshih-ot-voyn
https://zviazda.by/ru/news/20241113/1731491808-shkola-molodogo-uchenogo
https://zviazda.by/ru/news/20241112/1731401472-lukashenko-predlozhil-vuchichu-intensificirovat-belorussko-serbskie
https://zviazda.by/ru/news/20241112/1731394643-lukashenko-v-baku-pribyl-na-vsemirnyy-sammit-po-borbe-s-izmeneniem-klimata
https://zviazda.by/ru/news/20241113/1731491402-socopros-belorusy-preimushchestvenno-poluchayut-informaciyu-o-novostyah
https://zviazda.by/ru/news/20241113/1731480968-edinyy-imushchestvennyy-platezh
https://zviazda.by/ru/news/20241112/1731401857-kakie-celi-stoyat-pered-obnovlennym-centrom-socialnoy-realizacii-detey
https://zviazda.by/ru/news/20241112/1731408988-belorusskaya-ekspoziciya-pokorila-kitayskih-zakupshchikov-i-potrebiteley
https://zviazda.by/en/news/20241112/1731403070-samarkand-invites-you-journey-5-reasons-visit-jewel-east
https://zviazda.by/en/news/20241112/1731403657-local-history-spiritual-matter
https://zviazda.by/en/news/20241112/1731404993-belarusian-literature-world
https://zviazda.by/en/news/20241112/1731406062-forgotten-russian-writer-liberated-belarus
https://zviazda.by/en/news/20241112/1731406663-discovery-new-medical-publicist-opens
https://zviazda.by/en/news/20240806/1722929348-minsk-they-also-joke-english
https://zviazda.by/en/news/20241030/1730291735-artem-makarov-everything-possible-theatre-now-and-it-happening
https://zviazda.by/ru/news/20241112/1731406047-v-mogileve-nagradili-pobediteley-konkursa-otkryvaem-belarus
https://zviazda.by/ru/news/20241112/1731405798-sergeenko-na-rassmotrenii-v-palate-predstaviteley-nahoditsya-23
https://zviazda.by/ru/news/20241112/1731405690-v-belarusi-otmechaetsya-rost-vkladov-v-rublyah-i-snizhenie-v-valyute
https://zviazda.by/ru/news/20241112/1731405068-lukashenko-na-vstreche-s-prezidentom-zimbabve-nam-predstoit-eshche-nemalo
https://zviazda.by/ru/news/20241112/1731404726-snezhno-ledovaya-industriya-kitaya-demonstriruet-stremitelnyy-rost
https://zviazda.by/ru/news/20241112/1731404484-pogoda-vperedi-zyabkie-tumany
https://zviazda.by/ru/news/20241112/1731403646-marafon-edinstva-s-pinskim-akcentom
https://zviazda.by/ru/news/20241112/1731402354-kuda-vlozhit-svoi-finansy-chtoby-ih-priumnozhit
https://zviazda.by/ru/news/20241111/1731311450-lukashenko-11-12-noyabrya-sovershit-vizit-v-azerbaydzhan-dlya-uchastiya-vo
https://zviazda.by/ru/news/20241112/1731393810-poteri-i-vozvrashcheniya-nacionalnogo-hudozhestvennogo-muzeya
https://zviazda.by/ru/news/20241112/1731391896-na-fondovyh-birzhah-kitaya-zaregistrirovano-svyshe-53-tysyachi-kompaniy
https://zviazda.by/ru/news/20241111/1731335830-mts-yunisef-i-minobr-prezentovali-proekt-metodicheskogo-posobiya-dlya-shkol
https://zviazda.by/ru/news/20241111/1731325786-predlozheniya-v-zakonodatelstvo-i-organizaciya-ostanovochnogo-punkta
https://zviazda.by/ru/news/20241111/1731325069-kochanova-provodit-lichnyy-priem-grazhdan-v-rossonah
https://zviazda.by/ru/news/20241111/1731319793-v-belarusi-bolee-chem-na-99-zavershili-uborku-ovoshchey
https://zviazda.by/ru/news/20241111/1731319671-minekonomiki-o-planah-po-stroitelstvu-zhilya-na-pyatiletku
https://zviazda.by/ru/news/20241111/1731317023-segodnya-mozhno-obratitsya-v-obshchestvennye-priemnye-s-voprosami-ceny
https://zviazda.by/ru/news/20241111/1731312557-socopros-absolyutnoe-bolshinstvo-belorusov-doveryayut-prezidentu-respubliki
https://zviazda.by/ru/news/20241111/1731304597-komu-zhdat-rosta-zarplat-v-2025-godu
https://zviazda.by/ru/news/20241111/1731312372-rybakov-rasskazal-budet-li-belaruskaliy-dobivatsya-snyatiya-sankciy
https://zviazda.by/ru/news/20241111/1731312184-novyy-kitayskiy-istrebitel-nevidimku-predstavyat-na-aviasalone-v-chzhuhae
https://zviazda.by/ru/news/20241111/1731311958-ishchem-modnoe-palto-v-kollekciyah-belorusskih-brendov
https://zviazda.by/ru/news/20241107/1730969625-lukashenko-priehal-na-chempionat-po-kolke-drov-sredi-zhurnalistov
https://zviazda.by/ru/news/20241111/1731311223-belstat-rasskazal-o-dohodah-i-socialnom-rassloenii-v-belarusi
https://zviazda.by/ru/news/20241111/1731311095-beloruska-macko-stala-pyatikratnoy-chempionkoy-mira-po-sambo
https://zviazda.by/ru/news/20241111/1731310736-beloruska-shut-vyigrala-bronzu-chempionata-mira-po-sambo
https://zviazda.by/ru/news/20241111/1731310545-v-kitae-nachalsya-priem-zayavok-na-lunnyy-grunt
https://zviazda.by/ru/news/20241031/1730359103-ryad-izmeneniy-po-naznacheniyu-i-polucheniyu-pensiy-prodolzhenie-programmy
https://zviazda.by/ru/news/20241107/1730967321-zhilishchnyy-kvadrat-v-sobstvennost
https://zviazda.by/ru/news/20241111/1731304328-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20241024/1729753460-vysokiy-spros-diktuet-ceny
https://zviazda.by/ru/news/20241109/1731138358-o-chyom-molchat-muzhchiny-znanie-etih-sekretov-ukrepyat-vashi-otnosheniya
https://zviazda.by/ru/news/20241107/1730977168-kakaya-obuv-v-trende-etoy-osenyu
https://zviazda.by/ru/news/20241107/1730976485-v-sinczyane-nahoditsya-velikaya-stena-podzemnyh-vod
https://zviazda.by/ru/news/20241107/1730976244-kak-izbavitsya-ot-gryzunov-v-dome
https://zviazda.by/ru/news/20241107/1730975351-v-pekine-predstavili-izobrazheniya-marok-po-sluchayu-sleduyushchego-goda
https://zviazda.by/ru/news/20241107/1730975094-v-kitae-zafiksirovan-znachitelnyy-rost-chisla-zaryadnyh-kolonok-dlya
https://zviazda.by/ru/news/20241107/1730974675-tretiy-chempionat-po-kolke-drov-sredi-smi-prohodit-v-minskom-rayone
https://zviazda.by/ru/news/20241107/1730974465-volfovich-prinimaet-uchastie-vo-vstreche-sekretarey-sovbezov-stran-sng-v
https://zviazda.by/ru/news/20241107/1730974340-v-belarusi-startoval-sbor-podpisey-dlya-vydvizheniya-kandidatov-v
https://zviazda.by/ru/news/20241107/1730974140-golovchenko-otkryl-novuyu-polikliniku-v-smolevichah
https://zviazda.by/ru/news/20241107/1730973961-v-osipovichah-poyavilas-shkola-so-znakom-kachestva
https://zviazda.by/ru/news/20241107/1730973680-podarok-dlya-zhiteley-gomelshchiny-vazhneyshiy-transportnyy-uzel
https://zviazda.by/ru/news/20241107/1730973308-v-polockom-rayone-otkryli-posle-rekonstrukcii-uchastok-dorogi-r-46
https://zviazda.by/ru/news/20241107/1730972968-molodye-kitaycy-vybirayut-byudzhetnye-varianty-puteshestviy
https://zviazda.by/ru/news/20241107/1730972663-kubrakov-veterany-mvd-odno-celoe-s-deystvuyushchimi-sotrudnikami-milicii
https://zviazda.by/ru/news/20241107/1730969473-prezident-pozdravil-belorusov-s-dnem-oktyabrskoy-revolyucii
https://zviazda.by/ru/news/20241106/1730883647-kak-gretsya-chtoby-ne-zagoretsya
https://zviazda.by/ru/news/20241106/1730901433-kak-kompartiya-privela-kitay-k-mirovomu-liderstvu
https://zviazda.by/ru/news/20241106/1730892159-videoservis-mts-tv-predlagaet-podborku-filmov-s-populyarnymi-aktrisami
https://zviazda.by/ru/news/20241106/1730890959-lukashenko-oficialno-otkryl-v-minske-basseyn-mezhdunarodnogo-standarta
https://zviazda.by/ru/news/20241106/1730890747-lukashenko-ob-otnosheniyah-belarusi-i-kitaya-my-dlya-vas-nadezhnye-druzya
https://zviazda.by/ru/news/20241106/1730886869-v-grodno-v-molodom-mikrorayone-otkryli-samyy-bolshoy-detskiy-sad-oblasti
https://zviazda.by/ru/news/20241106/1730886470-pochemu-v-belarusi-do-sih-por-otmechayut-den-oktyabrskoy-revolyucii
https://zviazda.by/ru/news/20241106/1730886366-v-brestskom-rayone-vveli-v-stroy-novyy-dom-dlya-rabotnikov
https://zviazda.by/ru/news/20241106/1730886101-kak-cum-minsk-otprazdnoval-60-letniy-yubiley
https://zviazda.by/ru/news/20241106/1730885884-v-kitae-sformirovany-neskolko-portovyh-klasterov-mirovogo-urovnya
https://zviazda.by/ru/news/20241106/1730885713-kak-ukrepit-zdorove-v-pozhilom-vozraste
https://zviazda.by/ru/news/20241106/1730884328-v-mogileve-obsudili-deyatelnost-organov-samoupravleniya
https://zviazda.by/ru/news/20241106/1730878269-chem-privlech-lyudey-k-derevne
https://zviazda.by/ru/news/20241106/1730877269-interesnaya-istoriya-volozhinskoy-ieshivy-otkryvsheysya-posle-rekonstrukcii
https://zviazda.by/ru/news/20241105/1730814729-internet-magazin-fishka-remonta-polnyy-spektr-materialov-dlya-stroitelstva
https://zviazda.by/ru/page/respublikanskiy-spisok-ekstremistskih-materialov
https://zviazda.by/ru/news/20241105/1730804754-golovchenko-soyuznoe-stroitelstvo-pomogaet-belarusi-i-rossii-effektivno
https://zviazda.by/ru/news/20241105/1730804458-lukashenko-ob-izbiratelnoy-kampanii-v-belarusi
https://zviazda.by/ru/news/20241104/1730711600-lukashenko-soglasoval-naznachenie-novyh-rukovoditeley-v-belneftehim-i-na
https://zviazda.by/ru/news/20241105/1730796423-lukashenko-belarus-i-tulskaya-oblast-rossii-sposobny-dostich-tovarooborota
https://zviazda.by/ru/news/20241105/1730796255-v-mogileve-sozdana-oblastnaya-komissiya-po-vyboram-prezidenta-respubliki
https://zviazda.by/ru/news/20241104/1730705990-chleny-soveta-respubliki-provedut-11-noyabrya-edinyy-den-priema-grazhdan-v
https://zviazda.by/ru/news/20241105/1730794006-karankevich-o-zadachah-dlya-novogo-predsedatelya-belneftehima
https://zviazda.by/ru/news/20241105/1730793677-chto-posmotret-5-noyabrya
https://zviazda.by/ru/news/20241105/1730793573-kitayskiy-proizvoditel-elektromobiley-byd-vpervye-oboshel-tesla-po
https://zviazda.by/ru/news/20241105/1730793384-golovchenko-zasedanie-soveta-ministrov-soyuznogo-gosudarstva-proydet-v
https://zviazda.by/ru/news/20241105/1730792201-pochti-44-mln-tonn-saharnoy-svekly-nakopali-v-belarusi
https://zviazda.by/ru/news/20241105/1730792054-gid-po-modnym-sumkam-chto-seychas-v-trende
https://zviazda.by/ru/news/20241105/1730791626-pogoda-mokryy-sneg-i-gololed
https://zviazda.by/ru/news/20241105/1730791157-obem-morskoy-ekonomiki-kitaya-dostig-77-trilliona-yuaney
https://zviazda.by/ru/news/20241101/1730440902-u-kogo-i-na-skolko-vyrastet-pensiya
https://zviazda.by/ru/news/20241102/1730544316-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20241105/1730788820-nash-tridcatyy-listapad
https://zviazda.by/ru/news/20241104/1730722031-v-kazahstane-vvedena-novaya-viza-dlya-sovremennyh-kochevnikov
https://zviazda.by/ru/news/20241104/1730719193-smartfon-honor-x9b-s-vygodoy-do-40-v-mts
https://zviazda.by/ru/news/20241104/1730718743-regionalnye-otbory-k-konkursam-slavyanskogo-bazara-v-vitebske-startuyut-20
https://zviazda.by/ru/news/20241104/1730717311-belarus-zainteresovana-v-ukreplenii-svyazey-s-panafrikanskim-parlamentom
https://zviazda.by/ru/news/20241104/1730717195-v-klimovichah-zolotaya-pchelka-razdala-nagrady
https://zviazda.by/ru/news/20241104/1730706267-nachalsya-rabochiy-vizit-belorusskoy-parlamentskoy-delegacii-v-yuar
https://zviazda.by/ru/news/20241104/1730716476-lukashenko-o-kadrovom-obespechenii-sistemy-mid
https://zviazda.by/ru/news/20241031/1730361923-lukashenko-prodlil-programmu-semeynogo-kapitala-ukazom-predusmotreno
https://zviazda.by/ru/news/20241104/1730709181-v-belarusi-s-nachala-pyatiletki-postroeno-bolee-70-detskih-sadov-i-bolee-20
https://zviazda.by/ru/news/20241101/1730458202-golovchenko-prizval-predpriyatiya-holdinga-belresursy-narashchivat
https://zviazda.by/ru/news/20241104/1730705722-v-chendu-predstavlen-pervyy-kitayskiy-ultralegkiy-chelovekopodobnyy-robot
https://zviazda.by/ru/news/20241104/1730705542-na-razlichnye-posobiya-semyam-v-2025-godu-predusmotreno-br32-mlrd
https://zviazda.by/ru/news/20241104/1730705368-volfovich-na-konferenciyu-po-evraziyskoy-bezopasnosti-v-minsk-priehali-vse
https://zviazda.by/ru/news/20241102/1730542809-kak-razvivaetsya-aviacionnaya-otrasl
https://zviazda.by/ru/news/20241102/1730544666-kitayskiy-teatr-teney-sushchestvuet-uzhe-bolee-2000-let
https://zviazda.by/ru/news/20241102/1730546078-zashchititsya-ot-holoda-i-podcherknut-individualnost
https://zviazda.by/ru/news/20241102/1730543978-10-prostyh-sposobov-kotorye-uluchshat-rabotu-vashego-mozga
https://zviazda.by/ru/news/20241102/1730543425-para-iz-nankina-delaet-snimki-kory-derevev
https://zviazda.by/ru/news/20241102/1730543102-v-provincii-hubey-proshli-sorevnovaniya-na-drakonih-lodkah
https://zviazda.by/ru/news/20241102/1730546253-infekcionist-o-vakcine-i-sezonnyh-virusah
https://zviazda.by/ru/news/20241102/1730542969-cik-dlya-provedeniya-vyborov-prezidenta-v-territorialnye-komissii-vydvinuto
https://zviazda.by/ru/news/20241102/1730535100-samaya-glavnaya-nagrada-v-zhizni-evgeniya-zolotogo
https://zviazda.by/ru/news/20241101/1730457116-v-kitae-nachalos-stroitelstvo-pervoy-v-mire-proizvodstvennoy-bazy
https://zviazda.by/ru/news/20241101/1730460778-mts-tv-predlagaet-podborku-filmov-kotorye-poshchekochut-nervy
https://zviazda.by/ru/news/20241101/1730458382-uborka-ovoshchey-v-belarusi-zavershena-na-97
https://zviazda.by/ru/news/20241031/1730362090-minsk-prinimaet-vtoruyu-mezhdunarodnuyu-konferenciyu-po-evraziyskoy
https://zviazda.by/ru/news/20241101/1730456841-nok-belarusi-prinimaet-uchastie-v-xxvii-generalnoy-assamblee-anok-v
https://zviazda.by/ru/news/20241101/1730456415-4-10-noyabrya-deputaty-palaty-predstaviteley-rabotayut-v-izbiratelnyh
https://zviazda.by/ru/news/20241101/1730454833-novyy-sezon-na-mire
https://zviazda.by/ru/news/20241101/1730453061-kartun-o-regionalnom-razvitii-na-blizhayshuyu-pyatiletku
https://zviazda.by/ru/news/20241101/1730452932-belorus-rumyancev-stal-bronzovym-prizerom-yunosheskogo-pervenstva-mira-po
https://zviazda.by/ru/news/20241101/1730452808-volfovich-belarus-ne-na-slovah-na-dele-dokazyvaet-chto-my-za-mir-bezopasnoe
https://zviazda.by/ru/news/20241101/1730446867-pochemu-vsemirnyy-bank-uluchshil-prognoz-po-vvp-dlya-belarusi
https://zviazda.by/ru/news/20241101/1730445308-sergeenko-provedet-11-noyabrya-lichnyy-priem-grazhdan
https://zviazda.by/ru/news/20241031/1730374188-gde-v-pekine-razgovarivayut-po-belorusski
https://zviazda.by/ru/news/20241101/1730443463-yubileynyy-xxx-minskiy-mezhdunarodnyy-kinofestival-listapad-startuet-v
https://zviazda.by/ru/news/20241101/1730443284-razmery-gosposobiy-semyam-s-detmi-uvelichivayutsya-s-1-noyabrya
https://zviazda.by/ru/news/20241101/1730443148-razmer-bpm-uvelichivaetsya-s-1-noyabrya
https://zviazda.by/ru/news/20241101/1730443033-robosobaki-pomogayut-ubirat-musor-s-gory-tayshan
https://zviazda.by/ru/news/20241101/1730442853-kochanova-my-vsegda-gotovy-k-dialogu
https://zviazda.by/ru/news/20241101/1730442556-v-vyhodnye-ozhidaetsya-pervyy-sneg
https://zviazda.by/ru/news/20241101/1730442305-belarus-i-vengriya-aktivizirovali-vzaimodeystvie
https://zviazda.by/ru/news/20241101/1730442147-proshlo-zasedanie-cik
https://zviazda.by/ru/news/20241101/1730441874-pribyl-vedushchih-promyshlennyh-predpriyatiy-kitaya-prevysil-5-trillionov
https://zviazda.by/ru/news/20241101/1730441538-snopkov-ideologiya-sleduyushchey-pyatiletki-debyurokratizaciya-v-shirokom
https://zviazda.by/ru/news/20241030/1730270421-snizit-avariynost-i-travmatizm
https://zviazda.by/ru/news/20241031/1730360161-egor-shchelkanov-luchshe-imet-odno-zoloto-chem-dva-serebra
https://zviazda.by/ru/news/20241031/1730367797-ryzhenkov-i-lavrov-obsudili-razrabotku-dokumenta-o-garantiyah-bezopasnosti
https://zviazda.by/ru/news/20241031/1730367678-fotoelektricheskaya-promyshlennost-kitaya-demonstriruet-rekordnyy-rost
https://zviazda.by/ru/news/20241031/1730367483-natalya-dergach-prinyat-i-vyslushat-kazhdogo
https://zviazda.by/ru/news/20241031/1730367241-dialogovaya-ploshchadka-edinomyshlennikov-v-briks-net-vedushchih-i-vedomyh
https://zviazda.by/ru/news/20241031/1730366427-tradiciya-gotovit-horoshih-pedagogov
https://zviazda.by/ru/news/20241031/1730366174-v-14-shkolah-v-raznyh-regionah-belarusi-rabotayut-transportnye-klassy
https://zviazda.by/ru/news/20241031/1730365936-forum-iskusstvennyy-intellekt-v-belarusi-znachitelno-omolodilsya
https://zviazda.by/ru/news/20241031/1730365530-kubrakov-mvd-belarusi-gotovo-k-prodolzheniyu-partnerstva-s-serbskimi
https://zviazda.by/ru/news/20241031/1730361605-stanet-li-mogilevshchina-turisticheskoy-mekkoy
https://zviazda.by/en/news/20241030/1730296256-belarusian-literature-world
https://zviazda.by/en/news/20241030/1730295625-poet-and-playwright-byaroza-kartuzskaya
https://zviazda.by/en/news/20241030/1730294548-russian-writers-18th-early-20th-centuries-natives-modern-mogilev-region
https://zviazda.by/en/news/20241030/1730293063-right-or-left-thinking-we-get-birth
https://zviazda.by/en/news/20241030/1730292672-zhong-guo-wen-xue-ping-lun-jia-ying-tian-shi-yan-zhong-de-yi-mo-sha-mi-ya
https://zviazda.by/en/news/20240905/1725541991-formula-effective-leader
https://zviazda.by/en/news/20240806/1722925617-our-weapon-love-sword-and-memory-our-ancestors-shield
https://zviazda.by/ru/news/20241030/1730289014-pogranichniki-stran-sng-obsuzhdayut-protivodeystvie-transgranichnoy
https://zviazda.by/ru/news/20241030/1730288869-shenchzhen-stremitsya-k-razvitiyu-industrii-iskusstvennogo-intellekta-nev
https://zviazda.by/ru/news/20241030/1730288685-respublikanskiy-pravovoy-priem-proydet-31-oktyabrya-po-vsey-strane
https://zviazda.by/ru/news/20241030/1730287825-mts-rasshiryaet-geografiyu-lte
https://zviazda.by/ru/news/20241030/1730288524-sergeenko-protiv-belarusi-nedruzhestvennymi-stranami-otkryto-vedetsya
https://zviazda.by/ru/news/20241030/1730286828-starty-kotorye-obedinyayut
https://zviazda.by/ru/news/20241030/1730286331-znat-uroven-lipidov-i-glyukozy-izmeryat-davlenie-i-brosit-kurit
https://zviazda.by/ru/news/20241030/1730279981-10-novyh-kitayskih-kosmonavtov-gotovyatsya-k-vysadke-na-lunu
https://zviazda.by/ru/news/20241029/1730193717-lukashenka-aguchyu-galounae-abyacanne-narodu-belarusi-u-peradvybarchy
https://zviazda.by/ru/news/20241030/1730278197-golovchenko-belarus-i-siriyu-svyazyvayut-podlinnaya-druzhba-i-davnie
https://zviazda.by/ru/news/20241030/1730276219-problemy-voprosy-predlozheniya
https://zviazda.by/ru/news/20241030/1730272179-prezentovat-stranu-cherez-krasotu
https://zviazda.by/ru/news/20241029/1730209615-korotkevicha-izdali-v-azerbaydzhane
https://zviazda.by/ru/news/20241029/1730195207-shkolnikov-priglasili-v-nauku
https://zviazda.by/ru/news/20241028/1730106778-lukashenko-ne-isklyuchaet-uvelicheniya-obemov-finansirovaniya-rossiey
https://zviazda.by/ru/news/20241029/1730191681-ryzhenkov-u-belarusi-i-sirii-est-potencial-dlya-ukrepleniya-politicheskogo
https://zviazda.by/ru/news/20241029/1730192504-sergeenko-sotrudnichestvo-belarusi-i-serbii-baziruetsya-na-vzaimoponimanii
https://zviazda.by/ru/news/20241029/1730190514-pogoda-zhdem-predzime
https://zviazda.by/ru/news/20241029/1730189861-golovchenko-i-manturov-dogovorilis-ob-uglublenii-lokalizacii
https://zviazda.by/ru/news/20241029/1730189471-transportnaya-set-shos-stanovitsya-vse-bolee-razvetvlennoy
https://zviazda.by/ru/news/20241029/1730188717-chem-udivlyaet-borisovshchina
https://zviazda.by/ru/news/20241029/1730187017-marafon-edinstva-risoval-svoyu-yarkuyu-istoriyu-v-zhizni-zhlobinshchiny
https://zviazda.by/ru/news/20241029/1730181214-opredeleny-luchshie-otechestvennye-izobreteniya
https://zviazda.by/ru/news/20241028/1730119434-v-seti-salonov-i-internet-magazine-mts-nachalis-prodazhi-novogo-plansheta
https://zviazda.by/ru/news/20241028/1730097251-snopkov-rasskazal-ob-uluchshenii-prognoza-vsemirnogo-banka-o-roste-vvp
https://zviazda.by/ru/news/20241028/1730107143-psiholog-effektivnye-psihologicheskie-priyomy-na-kazhdyy-den-kotorye
https://zviazda.by/ru/news/20241028/1730092156-galstuk-ochki-i-belye-noski-kak-s-pomoshchyu-prostyh-aksessuarov-sozdat
https://zviazda.by/ru/news/20241028/1730092588-s-chem-belarus-idet-v-briks-i-pochemu-nam-kak-i-vsey-planete-ochen-nuzhen
https://zviazda.by/ru/news/20241028/1730092821-lukashenko-ne-somnevaetsya-chto-kampaniya-po-vyboram-v-belarusi-proydet
https://zviazda.by/ru/news/20241028/1730102610-sotni-tysyach-sazhencev-vysadili-predstaviteli-profsoyuzov-po-vsey-strane-v
https://zviazda.by/ru/news/20241028/1730101739-vyshla-novaya-kniga-o-mazurove
https://zviazda.by/ru/news/20241028/1730100462-v-kitae-aktivno-primenyayutsya-konteynernye-fermy
https://zviazda.by/ru/news/20241028/1730096588-evgeniy-arendarevich-ne-vse-v-kino-opredelyaetsya-dengami-i-ekonomicheskoy
https://zviazda.by/ru/news/20241024/1729752480-odin-rayon-odin-proekt-impuls-razvitiya
https://zviazda.by/ru/news/20241028/1730094184-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20241022/1729586773-ot-glubokogo-k-drue-cherez-braslav
https://zviazda.by/ru/news/20241024/1729754892-chto-izmenitsya-v-sfere-obrazovaniya
https://zviazda.by/ru/news/20241024/1729755782-lukashenko-v-kazani-pribyl-na-sammit-briks-v-formate-autrichplyus
https://zviazda.by/ru/news/20241024/1729749288-lukashenko-o-briks-mesto-belarusi-v-etom-kollektive
https://zviazda.by/ru/news/20241024/1729786846-kazahstan-otmechaet-den-respubliki
https://zviazda.by/ru/news/20241025/1729850443-eho-kannskogo-festivalya-mts-tv-predlagaet-kinolenty-so-zvezdami-anory
https://zviazda.by/ru/news/20241024/1729747910-data-vyborov-prezidenta-respubliki-belarus-naznachena-na-26-yanvarya-2025
https://zviazda.by/ru/news/20241024/1729760798-sergeenko-mezhdu-belarusyu-i-kitaem-dostignut-ochen-vysokiy-uroven
https://zviazda.by/ru/news/20241024/1729759821-v-kitae-razrabotali-pervyy-v-mire-cifrovoy-pet-shlem
https://zviazda.by/ru/news/20241024/1729759651-golovchenko-posetit-s-rabochim-vizitom-sankt-peterburg
https://zviazda.by/ru/news/20241024/1729758340-uchashchiesya-shkoly-mira-i-liceya-mvd-posetili-dvorec-nezavisimosti
https://zviazda.by/ru/news/20241024/1729757774-orden-brazilii-vruchili-belorusskomu-pedagogu
https://zviazda.by/ru/news/20241024/1729757145-na-vyborah-prezidenta-budut-obrazovany-153-territorialnye-i-bolee-5-tys
https://zviazda.by/ru/news/20241022/1729574490-natalya-kochanova-vazhno-byt-na-ostrie-zadach
https://zviazda.by/ru/news/20241021/1729508479-lukashenko-predlozhil-postroit-skorostnye-linii-k-gorodam-sputnikam-minska
https://zviazda.by/ru/news/20241023/1729697070-kazahstan-voshel-v-spisok-luchshih-stran-dlya-puteshestviy
https://zviazda.by/ru/news/20241023/1729681795-mesyac-honor-pokupayte-devaysy-s-vygodoy-do-40-v-mts
https://zviazda.by/ru/news/20241022/1729608919-osen-v-podnebesnoy
https://zviazda.by/ru/news/20241022/1729588476-karmen-dlya-detey-i-ne-tolko-pokazhet-v-belarusi-moskovskiy-teatr
https://zviazda.by/ru/news/20241022/1729587401-snopkov-vneshnetorgovye-potoki-demonstriruyut-rost-nesmotrya-na-sankcii
https://zviazda.by/ru/news/20241022/1729586979-kochanova-belorusskaya-ekonomicheskaya-model-dokazyvaet-svoyu-effektivnost
https://zviazda.by/ru/news/20241022/1729576329-sobirayte-i-sohranyayte-dlya-istorii
https://zviazda.by/ru/news/20241022/1729583862-tysyachi-goryachih-serdec-uchastnikov-marafona-edinstva
https://zviazda.by/ru/news/20241022/1729580052-studenty-bgut-prodemonstrirovali-horoshuyu-fizicheskuyu-podgotovku
https://zviazda.by/ru/news/20241022/1729578716-s-rynka-dunczi-ezhednevno-otgruzhayut-60-tonn-ryby
https://zviazda.by/ru/news/20241022/1729578031-pravitelstvo-uvelichilo-finansirovanie-issledovaniy-gosstandarta
https://zviazda.by/ru/news/20241021/1729491959-prezident-pozdravil-muzhchin-s-dnem-otca
https://zviazda.by/ru/news/20241021/1729498816-mts-predlagaet-biznesu-smart-kassy-i-osobye-usloviya-ih-priobreteniya
https://zviazda.by/ru/news/20241021/1729500571-kakimi-sladkimi-novogodnimi-podarkami-poraduyut-nas-konditery
https://zviazda.by/ru/news/20241021/1729499687-obshchestvennyy-sovet-po-nravstvennosti-proshel-v-rasshirennom-formate
https://zviazda.by/ru/news/20241021/1729497475-okolo-32-mln-tonn-saharnoy-svekly-sobrano-v-belarusi
https://zviazda.by/ru/news/20241021/1729496557-resursy-regionov-privlekatelny-dlya-biznesa
https://zviazda.by/ru/news/20241021/1729495689-v-pekine-robot-povar-poluchil-razreshenie-na-rabotu
https://zviazda.by/ru/news/20241021/1729492810-pochemu-sozdat-novye-gibridy-kukuruzy-osobenno-vazhnaya-rabota
https://zviazda.by/ru/news/20241021/1729492496-kak-mnogozadachnost-vliyaet-na-pamyat-i-myshlenie
https://zviazda.by/ru/news/20241017/1729155948-lukashenko-o-rabote-polyarnikov-v-antarktide-vse-eti-meropriyatiya-nam
https://zviazda.by/ru/news/20241021/1729490936-na-uik-end-za-zhivymi-vitaminami
https://zviazda.by/ru/news/20241021/1729489170-nedelya-roditelskoy-lyubvi-horoshiy-povod-rasskazat-o-mame-i-pape
https://zviazda.by/ru/news/20241021/1729487982-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20241017/1729157130-den-materi-v-belarusi-priurochen-k-prazdniku-pokrova-presvyatoy-bogorodicy
https://zviazda.by/ru/news/20241015/1728982681-lukashenko-ekonomika-belarusi-pozvolyaet-napravit-bolshe-deneg-na
https://zviazda.by/ru/news/20241017/1729154490-proshla-vstrecha-predsedatelya-spb-so-studentami-agrariyami
https://zviazda.by/ru/news/20241017/1729155190-lukashenko-issledovaniya-belorusskih-polyarnikov-neobhodimo-primenyat-v
https://zviazda.by/ru/news/20241017/1729155021-vvp-belarusi-v-yanvare-sentyabre-vyros-na-45
https://zviazda.by/ru/news/20241017/1729152852-salat-s-fasolyu-i-vareniki-bez-muki
https://zviazda.by/ru/news/20241017/1729142168-zavershilsya-rabochiy-vizit-golovchenko-v-pakistan
https://zviazda.by/ru/news/20241017/1729152049-hokkeynaya-komanda-prezidenta-na-vsebelorusskoy-molodezhnoy-stroyke
https://zviazda.by/ru/news/20241017/1729150842-deputaty-palaty-predstaviteley-posetili-gomelshchinu
https://zviazda.by/ru/news/20241017/1729148819-kitay-poluchil-70-procentov-mirovyh-zakazov-na-stroitelstvo-ekologicheskih
https://zviazda.by/ru/news/20241017/1729146788-shagi-k-pobede-v-semeynom-konkurse
https://zviazda.by/ru/news/20241017/1729145006-pervyy-etap-repeticionnogo-testirovaniya-prohodit-v-belarusi
https://zviazda.by/ru/news/20241017/1729144056-chego-dostigla-otechestvennaya-farmacevtika
https://zviazda.by/ru/news/20241016/1729080106-dlya-kinomanov-i-lyuboznatelnyh-v-mts-tv-stali-dostupny-novye-telekanaly
https://zviazda.by/ru/news/20241015/1728985996-lukashenko-v-belarusi-prodolzhat-okazyvat-podderzhku-mnogodetnym
https://zviazda.by/ru/news/20241015/1728985021-krutoy-popytki-perepisat-nashu-istoriyu-stali-eshche-bolee-yarostnymi
https://zviazda.by/ru/news/20241015/1728983419-sergeenko-vozlozhil-cvety-k-memorialu-ola-v-svetlogorskom-rayone
https://zviazda.by/ru/news/20241015/1728976284-golovchenko-napravilsya-s-rabochim-vizitom-v-pakistan
https://zviazda.by/ru/news/20241015/1728968481-lukashenko-prinyal-s-dokladom-prezidenta-nok
https://zviazda.by/ru/news/20241015/1728980654-v-kitae-iz-yagod-godzhi-gotovyat-deserty-i-napitki
https://zviazda.by/ru/news/20241015/1728980453-federaciya-profsoyuzov-primet-aktivnoe-uchastie-v-vosstanovlenii-lesa-posle
https://zviazda.by/ru/news/20241015/1728980012-kakie-zabolevaniya-vsyo-eshchyo-neprosto-poddayutsya-terapii-kakie-uzhe
https://zviazda.by/ru/news/20241015/1728972720-put-k-hramu
https://zviazda.by/ru/news/20241015/1728978206-pogoda-nochyu-zamorozki-da-i-dnem-ne-zharko
https://zviazda.by/ru/news/20241015/1728976933-vo-vtornik-i-sredu-v-minske-proydet-seminar-innovacii-v-realnom-sektore
https://zviazda.by/ru/news/20241015/1728968928-sergeenko-eti-sportivnye-dostizheniya-yavlyayutsya-obrazcom-dlya
https://zviazda.by/ru/news/20241015/1728975628-yarkie-cveta-marafona-edinstva
https://zviazda.by/ru/news/20241015/1728973965-vengerskiy-cugcvang-nezavisimost-eto-ne-pro-evropu
https://zviazda.by/ru/news/20241014/1728882394-priroda-nadelila-nezhnye-zhenskie-serdca-nepovtorimym-chuvstvom-materinskoy
https://zviazda.by/ru/news/20241014/1728896513-internet-magazin-mts-stal-pobeditelem-konkursa-vybor-goda
https://zviazda.by/ru/news/20241014/1728895772-yana-psayla-predstavlyaet-belorusskuyu-literaturu
https://zviazda.by/ru/news/20241014/1728893632-uborka-kartofelya-v-selhozorganizaciyah-belarusi-zavershena-pochti-na-90
https://zviazda.by/ru/news/20241014/1728893219-kak-spravlyatsya-s-vygoraniem
https://zviazda.by/ru/news/20241014/1728892813-skolko-v-belarusi-poleznyh-iskopaemyh
https://zviazda.by/ru/news/20241014/1728890669-belarus-reshitelno-osuzhdaet-lyubye-proyavleniya-terrorizma
https://zviazda.by/ru/news/20241014/1728890193-kak-pravilno-otvechat-na-hamstvo-i-grubost
https://zviazda.by/ru/news/20241014/1728889603-golovchenko-provodit-peregovory-s-naslednym-princem-omana
https://zviazda.by/ru/news/20241014/1728889218-v-provincii-cinhay-nashli-drevnie-naskalnye-risunki
https://zviazda.by/ru/news/20241014/1728888796-golovchenko-vstretilsya-s-glavoy-mid-omana
https://zviazda.by/ru/news/20241014/1728887841-v-kitae-aktivno-razvivaetsya-mezhdunarodnaya-ekspress-dostavka
https://zviazda.by/ru/news/20241014/1728887014-zoya-melnikova-uchitel-eto-chelovek-kotoryy-vsyu-zhizn-uchitsya
https://zviazda.by/ru/news/20241014/1728885752-chem-segodnya-zhivet-vitebskiy-rayonnyy-centr-kultury-i-tvorchestva
https://zviazda.by/ru/news/20241014/1728884073-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20241014/1728883386-v-chem-cel-regionalnoy-integracii-kak-strana-spravilas-s-posledstviyami
https://zviazda.by/ru/news/20241011/1728634468-lukashenko-segodnya-rabotaet-na-maloy-rodine
https://zviazda.by/ru/news/20241011/1728649221-nakanune-dnya-materi-vdohnovlyaemsya-dushevnymi-kinoistoriyami-v-mts-tv
https://zviazda.by/ru/news/20241011/1728621815-miklashevich-provel-priem-grazhdan-v-vitebske
https://zviazda.by/ru/news/20241011/1728635871-v-pekine-obsudyat-deyatelnost-v-sfere-tele-i-radioveshchaniya
https://zviazda.by/ru/news/20241011/1728625972-igor-sergeenko-provel-vstrechu-seminar-s-pomoshchnikami-deputatov-palaty
https://zviazda.by/ru/news/20241011/1728634709-golovchenko-poseshchaet-arheologicheskiy-kompleks-na-menke
https://zviazda.by/ru/news/20241010/1728535480-zavershilsya-rabochiy-vizit-prezidenta-belarusi-aleksandra-lukashenko-v
https://zviazda.by/ru/news/20241011/1728633267-respublikanskiy-nauchno-prakticheskiy-centr-sporta-otmechaet-nebolshoy
https://zviazda.by/ru/news/20241011/1728629505-chem-sposobny-udivlyat-devushki
https://zviazda.by/ru/news/20241011/1728628595-patetychny-dzyonnik-pamyaci-na-telekanale-belarus-3
https://zviazda.by/ru/news/20241011/1728628079-pogoda-solnechno-eshche-budet-teplee-vryad-li
https://zviazda.by/ru/news/20241011/1728627729-bolee-141-tys-depozitnyh-schetov-po-programme-semeynyy-kapital-otkryto-v
https://zviazda.by/ru/news/20241011/1728627504-provinciya-czilin-postavlyaet-na-espart-gribnoy-delikates
https://zviazda.by/ru/news/20241011/1728625033-chto-kazhdyy-zhelayushchiy-mozhet-sdelat-chtoby-uluchshit-lyubimyy-gorod
https://zviazda.by/ru/news/20241011/1728624251-universalnyy-yazyk-kachestva
https://zviazda.by/ru/news/20241010/1728548390-kakie-zadachi-stoyat-pered-agrariyami-osenyu
https://zviazda.by/ru/news/20241010/1728559330-shkola-cifrovoy-gramotnosti-dlya-lyudey-starshego-vozrasta-ot-mts
https://zviazda.by/ru/news/20241010/1728550650-kakoy-kulturnyy-kod-zashifrovan-v-abradvee
https://zviazda.by/ru/news/20241010/1728550079-golovchenko-vruchil-gosnagrady-predstavitelyam-razlichnyh-sfer
https://zviazda.by/ru/news/20241010/1728549936-eto-ochen-nelegkaya-missiya-dobyvat-hleb
https://zviazda.by/ru/news/20241010/1728549362-turfan-stal-centrom-vinogradarstva-kitaya
https://zviazda.by/ru/news/20241010/1728549191-vladimir-percov-predstavil-kollektivu-ministerstva-informacii-novogo
https://zviazda.by/ru/news/20241010/1728548957-angelina-samoletova-tvorchestvo-zhivet-v-serdce-kazhdogo-cheloveka
https://zviazda.by/ru/news/20241010/1728546503-kak-uslugi-stanovyatsya-dostupnymi-v-kazhdom-ugolke-strany
https://zviazda.by/ru/news/20241010/1728541696-v-palate-predstaviteley-rassmotreli-novye-polnomochiya-notariusov-i
https://zviazda.by/ru/news/20241007/1728285383-krutoy-vozrozhdenie-polesya-stanet-nacionalnym-proektom-belarusi
https://zviazda.by/ru/news/20241009/1728484372-yadernyy-faktor-chto-neset-blago-ili-bedu-reshaet-tolko-chelovek
https://zviazda.by/ru/news/20241009/1728473865-krasota-razvitiya
https://zviazda.by/ru/news/20241004/1728020617-novuyu-knigu-doktora-gumena-prezentovali-v-memorialnom-muzee-yakuba-kolasa
https://zviazda.by/ru/news/20241007/1728298560-novye-smartfony-xiaomi-14t-serii-i-mix-flip-uzhe-v-mts
https://zviazda.by/ru/news/20241004/1728019935-ne-dopuskaem-chtoby-rebenka-vybirali-kak-v-magazine
https://zviazda.by/ru/news/20241007/1728289633-knigi-o-kitae-peredany-gimnazistam
https://zviazda.by/ru/news/20241007/1728285586-lukashenko-8-oktyabrya-v-moskve-primet-uchastie-v-sammite-sng
https://zviazda.by/ru/news/20241004/1728029376-lukashenko-v-pinskom-rayone-oznakomitsya-s-razvitiem-apk-i-socialnoy-sfery
https://zviazda.by/ru/news/20241004/1728033640-doklad-prezidentu-ob-itogah-uborochnoy-strana-budet-s-zernom-ozhidaemyy
https://zviazda.by/ru/news/20241007/1728282085-podvig-zoi-kosmodemyanskoy
https://zviazda.by/ru/news/20241007/1728281613-v-kitae-sobirayut-obshchestvennye-sredstva-dlya-zashchity-velikoy-kitayskoy
https://zviazda.by/ru/news/20241007/1728281303-oleg-orlov-glavnoe-vyzyvat-emocii-i-davat-slushatelyu-vozmozhnost-uslyshat
https://zviazda.by/ru/news/20241007/1728280227-karpenko-o-referendume-v-kazahstane-po-aes
https://zviazda.by/ru/news/20241007/1728280057-vyskazyvaniya-kotorye-inogda-sposobny-zamenit-pohod-k-psihologu
https://zviazda.by/ru/news/20241007/1728279786-v-kitae-aktivno-razvivaetsya-industriya-chelovekopodobnyh-robotov
https://zviazda.by/ru/news/20241004/1728019389-kakie-kachestva-dolzhny-byt-u-nastoyashchego-uchitelya
https://zviazda.by/ru/news/20241007/1728279244-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20241007/1728278770-kakovy-prioritety-v-sovremennom-doshkolnom-obrazovanii
https://zviazda.by/ru/news/20241004/1728034317-zaryadka-dlya-uma-v-mts-tv-dostupna-novaya-podborka-filmov-i-serialov
https://zviazda.by/ru/news/20241004/1728018170-belarus-i-azerbaydzhan-podpisali-dokumenty-o-sotrudnichestve
https://zviazda.by/ru/news/20241004/1728033082-belteleradiokompaniya-podgotovila-prazdnichnyy-efir-ko-dnyu-uchitelya
https://zviazda.by/ru/news/20241004/1728031005-kakoy-budet-pogoda-na-sleduyushchey-nedele
https://zviazda.by/ru/news/20241004/1728030611-vozmozhnost-rasskazat-o-mire-kotoryy-ya-lyublyu
https://zviazda.by/ru/news/20241004/1728017704-lukashenko-ob-otnosheniyah-s-azerbaydzhanom-my-ne-druzhim-protiv-tretih
https://zviazda.by/ru/news/20241004/1728029881-v-provincii-hebey-rasshiryaetsya-industriya-tovarov-dlya-domashnih
https://zviazda.by/ru/news/20241004/1728028610-sokratit-zahoronenie-othodov-i-naladit-ih-pererabotku
https://zviazda.by/ru/news/20241004/1728021262-sergey-kovalchuk-v-tom-chto-u-nas-segodnya-est-horoshiy-sportivnyy-rezerv
https://zviazda.by/ru/news/20241004/1728018722-v-minske-otkrylas-48-ya-mezhdunarodnaya-vystavka-vti-2024
https://zviazda.by/ru/news/20241002/1727858019-sergeenko-zakonoproekt-po-voprosam-veteranov-sbalansirovannyy-i-socialno
https://zviazda.by/ru/news/20241002/1727846566-lukashenko-dlya-nas-net-nedruzhestvennyh-narodov-i-vtorostepennyh-stran
https://zviazda.by/ru/news/20241002/1727872300-mts-poznakomit-lyudey-starshego-vozrasta-s-neyrosetyami
https://zviazda.by/ru/news/20241002/1727872513-mts-poznakomit-lyudey-starshego-vozrasta-s-neyrosetyami
https://zviazda.by/ru/news/20240930/1727684351-chto-nuzhno-znat-muzhchinam-o-zhenshchinah
https://zviazda.by/ru/news/20241002/1727860402-percov-na-vstrechah-s-molodezhyu-tema-informacionnoy-bezopasnosti-odna-iz
https://zviazda.by/ru/news/20241002/1727844954-novyy-posol-knr-peredal-privetstvie-lukashenko-ot-si-czinpina-i-podtverdil
https://zviazda.by/ru/news/20241002/1727858329-zakonoproekt-po-voprosam-obrazovaniya-prinyat-v-pervom-chtenii
https://zviazda.by/ru/news/20241002/1727846819-lukashenko-utverdil-vazhneyshie-prognoznye-parametry-razvitiya-belarusi-na
https://zviazda.by/ru/news/20241002/1727857249-deputaty-prinyali-vo-vtorom-chtenii-zakonoproekt-po-voprosam-veteranov
https://zviazda.by/ru/news/20241002/1727853494-profsoyuzy-apk-belarusi-egipta-i-rossii-zaklyuchili-soglashenie-o
https://zviazda.by/ru/news/20241002/1727852735-krupko-provel-priem-grazhdan-v-gomele
https://zviazda.by/ru/news/20241002/1727852491-byvshaya-traktoristka-nina-belyavskaya-o-tom-kak-v-svoi-85-ne-sidit-slozha
https://zviazda.by/ru/news/20241002/1727851833-chto-menyaetsya-dlya-ip-samozanyatyh-i-remeslennikov-s-1-oktyabrya
https://zviazda.by/ru/news/20241002/1727848052-kochanova-lyudi-starshego-pokoleniya-eto-nash-zolotoy-fond
https://zviazda.by/ru/news/20241002/1727847533-na-dolyu-obrabatyvayushchey-promyshlennosti-kitaya-prihoditsya-pochti-tret
https://zviazda.by/ru/news/20241002/1727847385-my-sdelaem-vse-chtoby-obespechit-regionalnuyu-yadernuyu-bezopasnost
https://zviazda.by/ru/news/20241002/1727847140-pervyy-gruz-po-severnomu-morskomu-puti-pribyl-v-belarus
https://zviazda.by/ru/news/20240930/1727687308-sergeenko-k-korrektirovke-zakonodatelstva-ob-obrazovanii-nuzhno-podhodit
https://zviazda.by/ru/news/20240930/1727685063-lukashenko-o-formule-sotrudnichestva-s-regionami-rossii-esli-chto-popalo
https://zviazda.by/ru/news/20241002/1727846358-kak-razvivaetsya-otechestvennoe-sadovodstvo
https://zviazda.by/ru/news/20241001/1727773908-chzhan-venchuan-kitaysko-belorusskoe-sotrudnichestvo-obrazec-mezhdunarodnyh
https://zviazda.by/ru/news/20240930/1727699184-start-prodazh-novoy-serii-smart-chasov-huawei-watch-gt-5-v-mts
https://zviazda.by/ru/news/20240930/1727685603-golovchenko-napravitsya-s-rabochim-vizitom-v-armeniyu
https://zviazda.by/ru/news/20240930/1727686933-ryzhenkov-na-vstreche-s-guterrishem-otmetil-neobhodimost-povysheniya-roli
https://zviazda.by/ru/news/20240930/1727672729-kak-budet-formirovatsya-byudzhet-na-2025-god
https://zviazda.by/ru/news/20240927/1727421202-lukashenko-prodolzhaet-obshchenie-so-studentami-v-formate-otkrytyy-mikrofon
https://zviazda.by/ru/news/20240930/1727679591-chto-ne-nuzhno-delat-na-ogorode
https://zviazda.by/ru/news/20240930/1727677693-samogo-bolshogo-nefritovogo-drakona-kultury-hunshan-nashli-na-severe-kitaya
https://zviazda.by/ru/news/20240930/1727676735-vystavka-navsegda-vmeste-prohodit-v-nacionalnoy-biblioteke-belarusi
https://zviazda.by/ru/news/20240930/1727676003-kitay-stal-odnim-iz-mirovyh-liderov-po-razvitiyu-zheleznoy-dorogi
https://zviazda.by/ru/news/20240930/1727675407-kak-gosudarstvo-zabotitsya-o-pozhilyh-lyudyah
https://zviazda.by/ru/news/20240927/1727414618-kakie-izmeneniya-zhdut-pravila-dorozhnogo-dvizheniya
https://zviazda.by/ru/news/20240930/1727673998-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20240819/1724082227-dvorec-respubliki-priglashaet-na-koncert-aleksandra-panayotova
https://zviazda.by/ru/news/20240927/1727415754-horoshiy-bonus-v-zhizni
https://zviazda.by/ru/news/20240930/1727673453-posetili-glavnuyu-sezonnuyu-yarmarku-stolicy-chto-i-pochem-pokupaem-etoy
https://zviazda.by/ru/news/20240927/1727417590-v-mid-podelilis-podrobnostyami-pervogo-dnya-vizita-ryzhenkova-v-nyu-york
https://zviazda.by/ru/news/20240927/1727426159-ryzhenkov-podtverdil-podderzhku-belarusyu-proekta-rezolyucii-ga-oon-o
https://zviazda.by/ru/news/20240927/1727424354-pervyy-forum-blogerov-belarusi-blogbay-nam-est-chto-skazat-startoval-v
https://zviazda.by/ru/news/20240927/1727423607-vyvoz-eksportnyh-belorusskih-gruzov-cherez-morskie-porty-rf-v-i-polugodii
https://zviazda.by/ru/news/20240927/1727422470-kochanova-zakony-dolzhny-byt-ponyatnymi-lyudyam
https://zviazda.by/ru/news/20240926/1727344084-lukashenko-rassmotrel-kadrovye-voprosy
https://zviazda.by/ru/news/20240927/1727420362-zavershilsya-priem-zayavok-na-uchastie-v-radiokonkurse-molodye-talanty
https://zviazda.by/ru/news/20240927/1727420037-pogoda-v-voskresene-sushchestvenno-poholodaet
https://zviazda.by/ru/news/20240927/1727418926-ekonomika-belarusi-na-uverennom-podyome
https://zviazda.by/ru/news/20240927/1727417874-kitay-poluchil-90-mirovyh-zakazov-na-stroitelstvo-sudov
https://zviazda.by/ru/news/20240926/1727333748-delegaciya-belarusi-vo-glave-s-ryzhenkovym-posetit-nyu-york-dlya-uchastiya
https://zviazda.by/ru/news/20240927/1727417260-rozhdennye-dlya-poleta
https://zviazda.by/ru/news/20240926/1727328207-kirill-nikitin-vdohnovlyayut-obychno-melochi
https://zviazda.by/ru/news/20240926/1727369333-v-belarusi-izmenili-poryadok-sdachi-ekzamenov-na-prava
https://zviazda.by/ru/news/20240926/1727333280-lukashenko-rasskazal-o-sozdannoy-v-belarusi-sisteme-oborony-gosudarstva
https://zviazda.by/ru/news/20240926/1727341210-beznakazannost-porozhdaet-vsedozvolennost-k-chemu-mozhet-privesti
https://zviazda.by/ru/news/20240926/1727340890-kochanova-uchastie-belorusskoy-delegacii-v-evraziyskom-zhenskom-forume-bylo
https://zviazda.by/ru/news/20240926/1727340349-profsoyuzy-obrazovaniya-i-nauki-belarusi-i-uzbekistana-podpisali-dogovor-o
https://zviazda.by/ru/news/20240926/1727338880-sergeenko-rabota-s-lyudmi-i-dialog-yavlyayutsya-opredelyayushchimi-v-rabote
https://zviazda.by/ru/news/20240926/1727338082-nayti-silu-i-pochuvstvovat-samobytnost-pozvolit-respublikanskaya-akciya
https://zviazda.by/ru/news/20240926/1727336616-glava-mid-belarusi-ob-otnosheniyah-s-litvoy-poka-ne-pozdno-nado-otoyti-ot
https://zviazda.by/ru/news/20240926/1727336137-sportivnaya-industriya-kitaya-demonstriruet-stremitelnyy-rost
https://zviazda.by/ru/news/20240926/1727335348-v-grodnenskoy-oblasti-startovala-dekada-zolotoy-vozrast
https://zviazda.by/ru/news/20240923/1727084251-krutoy-podcherknul-prioritetnost-razvitiya-sotrudnichestva-s-zimbabve
https://zviazda.by/ru/news/20240926/1727331238-minprom-rossiya-yavlyaetsya-ne-prosto-osnovnym-rynkom-sbyta-ploshchadkoy
https://zviazda.by/ru/news/20240926/1727328762-pyat-nasyshchennyh-dney-proveli-uchastniki-xvii-festivalya-molodezh-za
https://zviazda.by/ru/news/20240923/1727095632-smartfony-poco-h6-i-m6-serii-s-vygodoy-200-rubley-v-mts
https://zviazda.by/ru/news/20240919/1726752340-lukashenko-nazval-glavnyy-standart-vyborov-v-belarusi
https://zviazda.by/ru/news/20240923/1727081335-zasedanie-evraziyskogo-mezhpravsoveta-proydet-30-sentyabrya-1-oktyabrya
https://zviazda.by/ru/news/20240923/1727082474-ipatov-my-ne-dadim-nikomu-zabyt-ochernit-ili-falsificirovat-podvig-nashih
https://zviazda.by/ru/news/20240923/1727082267-volodin-prezidenty-belarusi-i-rossii-udelyayut-bolshoe-vnimanie-voprosam
https://zviazda.by/ru/news/20240923/1727081877-na-severe-kitaya-nashli-svyshe-sotni-nefritovyh-artefaktov-neolita
https://zviazda.by/ru/news/20240923/1727073883-sovet-parlamentskogo-sobraniya-soyuznogo-gosudarstva-posetil-buynichskoe
https://zviazda.by/ru/news/20240923/1727080986-v-kitae-zapushchen-polnostyu-avtomatizirovannyy-rybopromyshlennyy-terminal
https://zviazda.by/ru/news/20240923/1727080299-shuleyko-rasskazal-kakoy-urozhay-soberut-belorusskie-agrarii
https://zviazda.by/ru/news/20240923/1727080136-poet-eto-ryba-kotoraya-ne-umeet-molchat
https://zviazda.by/ru/news/20240923/1727076769-homenko-belarus-byla-i-ostaetsya-mirolyubivym-gosudarstvom
https://zviazda.by/ru/news/20240923/1727075987-alesya-kuznecova-lyubye-sobytiya-eto-rezultat-vybora
https://zviazda.by/ru/news/20240923/1727073261-kak-popast-v-studotryad-i-poluchit-tam-novuyu-specialnost
https://zviazda.by/ru/news/20240923/1727070216-vostochnyy-goroskop-na-sleduyushchuyu-nedelyu
https://zviazda.by/ru/news/20240920/1726832489-osen-s-mts-tv-premery-kotorye-ne-ostavyat-ravnodushnymi
https://zviazda.by/ru/news/20240919/1726752046-lukashenko-na-vstreche-s-pushilinym-podtverdil-gotovnost-razvivat
https://zviazda.by/ru/news/20240909/1725881887-pochemu-strany-afrikanskogo-kontinenta-ostayutsya-naibedneyshimi-v-mire
https://zviazda.by/ru/news/20240912/1726123874-radmila-rybakova-vazhno-ostavatsya-chelovekom
"""
# direct_URLs = list(pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/BLR/zviaza2.csv')['0'])
direct_URLs = text.split('\n')
source = 'zviazda.by'

#hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}



# direct_URLs = []
# for i in range(3):

#     sitemap = 'https://zviazda.by/be/sitemap.xml?page' + '=' + str(i+1)
#     print(sitemap)
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('loc')
#     print(item.text)
#     direct_URLs.append(item.text)

# # CHANGE HERE EVERY TIME WE UPDATE
# for i in item:
#     if '/202212' in i.text or '/202301' in i.text or '/202302' in i.text or '/202303' in i.text:
#         direct_URLs.append(i.text)

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = list(set(direct_URLs))
print(len(final_result))



url_count = 0
processed_url_count = 0

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header, verify=False)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem
            print("newsplease title: ", article['title'])

            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            

            # Get Main Text:
            try:
                maintext = soup.find('div', {'class': 'field-item even'}).text
                article['maintext'] = maintext.strip()

            except: 
                try:
                    soup.find('div', {'class': 'field-item even'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class': 'field-item even'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    article['maintext']  = article['maintext'] 
            print("newsplease maintext: ", article['maintext'][:50])
            
            # Get Date
            try:
                date = soup.find('meta', property = 'article:published_time')['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
            except:
                try:
                    date = soup.find('time').text
                    article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})
                except:
                    try:
                        date = soup.find('span', {'class' : 'date'}).text
                        article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})
                    except:
                        date = None
                        article['date_publish'] = date
            print("newsplease date: ", article['date_publish'])
            print(article['language'])
            
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'

            except:
                colname = 'articles-nodate'
            
            # Inserting article into the db:
            try:
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                pass
                print("DUPLICATE! Not inserted.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
