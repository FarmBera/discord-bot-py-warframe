# emoji for KO


def get_emoji(origin: str):
    item = origin.lower()

    # 7; general items
    if "riven" in item:
        return "<:rivenmod:1434448154371031152>"
    elif "kuva" in item:
        return "<:kuva:1434448114076356650>"
    elif "endo" in item:
        return "<:endo:1434448109097844766>"
    elif "arcane" in item or "artifact" in item:
        return "<:ArcaneEnhance:1434447901832253542>"
    elif "reactor" in item:
        return "<:OrokinReactor:1434447908450734180>"
    elif "catalyst" in item:
        return "<:OrokinCatalyst:1434447906823340032>"
    elif "ducat" in item:
        return "<:ducats:1434448107411607634>"
    elif "credit" in item:
        return "<:credits:1434448106111631471>"
    # 2; forma
    elif "forma" in item:
        return "<:forma:1434448112113549332>"
    elif "aura forma" in item:
        return "<:auraforma:1434448094316990585>"
    elif "umbra" in item:
        return "<:umbraforma:1434448156363587714>"

    # 5; adapter
    elif "exilus weapon" in item or "weaponutilityunlocker" in item:
        return "<:ExilusWeaponAdapter:1434447905304871004>"
    elif "exilus warframe" in item or "utilityunlocker" in item:
        return "<:ExilusWarframeAdapter:1434447903752982608>"
    elif "primary arcane" in item:
        return "<:PrimaryArcaneAdapter:1434447878675234916>"
    elif "secondary arcane" in item:
        return "<:SecondaryArcaneAdapter:1434447880898351155>"
    elif "melee arcane" in item:
        return "<:MeleeArcaneAdapter:1434447877018619944>"

    # 6; shard
    elif "crimson" in item:
        return "<:CrimsonArchonShard:1434447996145242122>"
    elif "azure" in item:
        return "<:AzureArchonShard:1434447994165661788>"
    elif "amber" in item:
        return "<:AmberArchonShard:1434447992231956523>"
    elif "emerald" in item:
        return "<:EmeraldArchonShard:1434448003959095328>"
    elif "topaz" in item:
        return "<:TopazArchonShard:1434448015132856430>"
    elif "violet" in item:
        return "<:VioletArchonShard:1434448017620209747>"

    # 5; void relics
    elif item in ["axi", "액시"]:
        return "<:AxiRelic:1434447931007696926>"
    elif item in ["lith", "리스"]:
        return "<:LithRelic:1434447932303872102>"
    elif item in ["meso", "메소"]:
        return "<:MesoRelic:1434447933708959796>"
    elif item in ["neo", "네오"]:
        return "<:NeoRelic:1434447940130177114>"
    elif item in ["requiem", "레퀴엠"]:
        return "<:RequiemRelic:1434447942516740130>"

    # 5; 3 day boosters
    elif "affinity" in item:
        return "<:3DayAffinity:1434447845548753020>"
    elif "mod" in item:
        return "<:3DayModDropChance:1434447848933687329>"
    elif "credit" in item:
        return "<:3DayCredit:1434447847054376960>"
    elif "resource drop" in item:
        return "<:3DayResourceDropChance:1434447851923963945>"
    elif "resource" in item:
        return "<:3DayResourceDropChance:1434447851923963945>"

    # warframes (circuit)
    elif "Ash" == origin:
        return "<:Ash:1438190262093480130>"
    elif "Atlas" == origin:
        return "<:Atlas:1438190264014471219>"
    elif "Banshee" == origin:
        return "<:Banshee:1438190265625219172>"
    elif "Baruuk" == origin:
        return "<:Baruuk:1438190267009077340>"
    elif "Caliban" == origin:
        return "<:Caliban:1438190268875542620>"
    elif "Chroma" == origin:
        return "<:Chroma:1438190270410789016>"
    elif "Citrine" == origin:
        return "<:Citrine:1438190272612794398>"
    elif "Cyte09" == origin:
        return "<:Cyte09:1438190274261156042>"
    elif "Dagath" == origin:
        return "<:Dagath:1438190276433674263>"
    elif "Dante" == origin:
        return "<:Dante:1438190278199738528>"
    elif "Ember" == origin:
        return "<:Ember:1438190625307754617>"
    elif "Equinox" == origin:
        return "<:Equinox:1438190282935107627>"
    elif "Excalibur" == origin:
        return "<:Excalibur:1438190284553981973>"
    elif "Frost" == origin:
        return "<:Frost:1438190286239961178>"
    elif "Gara" == origin:
        return "<:Gara:1438190287879929997>"
    elif "Garuda" == origin:
        return "<:Garuda:1438190289293545622>"
    elif "Gauss" == origin:
        return "<:Gauss:1438190290908221595>"
    elif "Grendel" == origin:
        return "<:Grendel:1438190292493926541>"
    elif "Gyre" == origin:
        return "<:Gyre:1438190294284898324>"
    elif "Harrow" == origin:
        return "<:Harrow:1438190296310612139>"
    elif "Hildryn" == origin:
        return "<:Hildryn:1438190297669439558>"
    elif "Hydroid" == origin:
        return "<:Hydroid:1438190299342966835>"
    elif "Inaros" == origin:
        return "<:Inaros:1438190301100507196>"
    elif "Ivara" == origin:
        return "<:Ivara:1438190302602199205>"
    elif "Khora" == origin:
        return "<:Khora:1438190304321605683>"
    elif "Koumei" == origin:
        return "<:Koumei:1438190306674737273>"
    elif "Kullervo" == origin:
        return "<:Kullervo:1438190308335681707>"
    elif "Lavos" == origin:
        return "<:Lavos:1438190309992566834>"
    elif "Limbo" == origin:
        return "<:Limbo:1438190311636734192>"
    elif "Loki" == origin:
        return "<:Loki:1438190313117323474>"
    elif "Mag" == origin:
        return "<:Mag:1438190315105161409>"
    elif "Mesa" == origin:
        return "<:Mesa:1438190317076615221>"
    elif "Mirage" == origin:
        return "<:Mirage:1438190318674514011>"
    elif "Nekros" == origin:
        return "<:Nekros:1438190320289583315>"
    elif "Nezha" == origin:
        return "<:Nezha:1438190322126684290>"
    elif "Nidus" == origin:
        return "<:Nidus:1438190323682640064>"
    elif "Nokko" == origin:
        return "<:Nokko:1438190325037269022>"
    elif "Nova" == origin:
        return "<:Nova:1438190326522052639>"
    elif "Nyx" == origin:
        return "<:Nyx:1438190327893721139>"
    elif "Oberon" == origin:
        return "<:Oberon:1438190330326286416>"
    elif "Octavia" == origin:
        return "<:Octavia:1438190332100481257>"
    elif "Oraxia" == origin:
        return "<:Oraxia:1438190333841117309>"
    elif "Protea" == origin:
        return "<:Protea:1438190335426826291>"
    elif "Qorvex" == origin:
        return "<:Qorvex:1438190336718405795>"
    elif "Revenant" == origin:
        return "<:Revenant:1438190338828144670>"
    elif "Rhino" == origin:
        return "<:Rhino:1438190340438753300>"
    elif "Saryn" == origin:
        return "<:Saryn:1438190342066278490>"
    elif "Sevagoth" == origin:
        return "<:Sevagoth:1438190343605452942>"
    elif "Styanax" == origin:
        return "<:Styanax:1438190345077915688>"
    elif "Temple" == origin:
        return "<:Temple:1438190346789060828>"
    elif "Titania" == origin:
        return "<:Titania:1438190348584226919>"
    elif "Trinity" == origin:
        return "<:Trinity:1438190350215676076>"
    elif "Valkyr" == origin:
        return "<:Valkyr:1438190352224751686>"
    elif "Vauban" == origin:
        return "<:Vauban:1438190353558536242>"
    elif "Volt" == origin:
        return "<:Volt:1438190355274141899>"
    elif "Voruna" == origin:
        return "<:Voruna:1438190356872302643>"
    elif "Wisp" == origin:
        return "<:Wisp:1438190358394703973>"
    elif "Wukong" == origin:
        return "<:Wukong:1438190359879614535>"
    elif "Xaku" == origin:
        return "<:Xaku:1438190361561534645>"
    elif "Yareli" == origin:
        return "<:Yareli:1438190363104772187>"
    elif "Zephyr" == origin:
        return "<:Zephyr:1438190364665315529>"

    # incarnon genesis
    elif "Ack & Brunt" == origin:
        return "<:AckBrunt:1438194050720333997>"
    elif "Angstrum" == origin:
        return "<:Angstrum:1438194052251127909>"
    elif "Anku" == origin:
        return "<:Anku:1438194053656084644>"
    elif "Atomos" == origin:
        return "<:Atomos:1438194055216631970>"
    elif "Bo" == origin:
        return "<:Bo:1438194056911126639>"
    elif "Boar" == origin:
        return "<:Boar:1438194058324476045>"
    elif "Boltor" == origin:
        return "<:Boltor:1438194060132089908>"
    elif "Braton" == origin:
        return "<:Braton:1438194061788844033>"
    elif "Bronco" == origin:
        return "<:Bronco:1438194063546515587>"
    elif "Burston" == origin:
        return "<:Burston:1438194065136160859>"
    elif "Ceramic Dagger" == origin:
        return "<:CeramicDagger:1438194066679529583>"
    elif "Cestra" == origin:
        return "<:Cestra:1438194068051198112>"
    elif "Dera" == origin:
        return "<:Dera:1438194069775057118>"
    elif "Despair" == origin:
        return "<:Despair:1438194071360372756>"
    elif "Dread" == origin:
        return "<:Dread:1438194073117917194>"
    elif "Dual Ichor" == origin:
        return "<:DualIchor:1438194074753700032>"
    elif "Dual Toxocyst" == origin:
        return "<:DualToxocyst:1438194076171243710>"
    elif "Furax" == origin:
        return "<:Furax:1438194077781721231>"
    elif "Furis" == origin:
        return "<:Furis:1438194079279222814>"
    elif "Gammacor" == origin:
        return "<:Gammacor:1438194080722190426>"
    elif "Gorgon" == origin:
        return "<:Gorgon:1438194112707825824>"
    elif "Hate" == origin:
        return "<:Hate:1438194114070839458>"
    elif "Kunai" == origin:
        return "<:Kunai:1438194115337654422>"
    elif "Lato" == origin:
        return "<:Lato:1438194117032017950>"
    elif "Latron" == origin:
        return "<:Latron:1438194118802018334>"
    elif "Lex" == origin:
        return "<:Lex:1438194120513556573>"
    elif "Magistar" == origin:
        return "<:Magistar:1438194121952202763>"
    elif "Miter" == origin:
        return "<:Miter:1438194123843567696>"
    elif "Nami Solo" == origin:
        return "<:NamiSolo:1438194125559300107>"
    elif "Okina" == origin:
        return "<:Okina:1438194127257993338>"
    elif "Paris" == origin:
        return "<:Paris:1438194128927064124>"
    elif "Sibear" == origin:
        return "<:Sibear:1438194130324029495>"
    elif "Sicarus" == origin:
        return "<:Sicarus:1438194132077252609>"
    elif "Skana" == origin:
        return "<:Skana:1438194133641728123>"
    elif "Soma" == origin:
        return "<:Soma:1438194135449342053>"
    elif "Strun" == origin:
        return "<:Strun:1438194137127190669>"
    elif "Sybaris" == origin:
        return "<:Sybaris:1438194138905575624>"
    elif "Torid" == origin:
        return "<:Torid:1438194140486701189>"
    elif "Vasto" == origin:
        return "<:Vasto:1438194142156161034>"
    elif "Zylok" == origin:
        return "<:Zylok:1438194143531630796>"

    else:
        return ""
