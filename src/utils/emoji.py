def get_emoji(item: str):
    item = item.lower()

    # 7; general items
    if "riven" in item:
        return "<:rivenmod:1434448154371031152>"
    elif "kuva" in item:
        return "<:kuva:1434448114076356650>"
    elif "endo" in item:
        return "<:endo:1434448109097844766>"
    elif "arcane enhancements" in item:
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
    elif "exilus weapon" in item:
        return "<:ExilusWeaponAdapter:1434447905304871004>"
    elif "exilus warframe" in item:
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
    elif "Ash" in item:
        return "<:Ash:1438190262093480130>"
    elif "Atlas" in item:
        return "<:Atlas:1438190264014471219>"
    elif "Banshee" in item:
        return "<:Banshee:1438190265625219172>"
    elif "Baruuk" in item:
        return "<:Baruuk:1438190267009077340>"
    elif "Caliban" in item:
        return "<:Caliban:1438190268875542620>"
    elif "Chroma" in item:
        return "<:Chroma:1438190270410789016>"
    elif "Citrine" in item:
        return "<:Citrine:1438190272612794398>"
    elif "Cyte09" in item:
        return "<:Cyte09:1438190274261156042>"
    elif "Dagath" in item:
        return "<:Dagath:1438190276433674263>"
    elif "Dante" in item:
        return "<:Dante:1438190278199738528>"
    elif "Ember" in item:
        return "<:Ember:1438190625307754617>"
    elif "Equinox" in item:
        return "<:Equinox:1438190282935107627>"
    elif "Excalibur" in item:
        return "<:Excalibur:1438190284553981973>"
    elif "Frost" in item:
        return "<:Frost:1438190286239961178>"
    elif "Gara" in item:
        return "<:Gara:1438190287879929997>"
    elif "Garuda" in item:
        return "<:Garuda:1438190289293545622>"
    elif "Gauss" in item:
        return "<:Gauss:1438190290908221595>"
    elif "Grendel" in item:
        return "<:Grendel:1438190292493926541>"
    elif "Gyre" in item:
        return "<:Gyre:1438190294284898324>"
    elif "Harrow" in item:
        return "<:Harrow:1438190296310612139>"
    elif "Hildryn" in item:
        return "<:Hildryn:1438190297669439558>"
    elif "Hydroid" in item:
        return "<:Hydroid:1438190299342966835>"
    elif "Inaros" in item:
        return "<:Inaros:1438190301100507196>"
    elif "Ivara" in item:
        return "<:Ivara:1438190302602199205>"
    elif "Khora" in item:
        return "<:Khora:1438190304321605683>"
    elif "Koumei" in item:
        return "<:Koumei:1438190306674737273>"
    elif "Kullervo" in item:
        return "<:Kullervo:1438190308335681707>"
    elif "Lavos" in item:
        return "<:Lavos:1438190309992566834>"
    elif "Limbo" in item:
        return "<:Limbo:1438190311636734192>"
    elif "Loki" in item:
        return "<:Loki:1438190313117323474>"
    elif "Mag" in item:
        return "<:Mag:1438190315105161409>"
    elif "Mesa" in item:
        return "<:Mesa:1438190317076615221>"
    elif "Mirage" in item:
        return "<:Mirage:1438190318674514011>"
    elif "Nekros" in item:
        return "<:Nekros:1438190320289583315>"
    elif "Nezha" in item:
        return "<:Nezha:1438190322126684290>"
    elif "Nidus" in item:
        return "<:Nidus:1438190323682640064>"
    elif "Nokko" in item:
        return "<:Nokko:1438190325037269022>"
    elif "Nova" in item:
        return "<:Nova:1438190326522052639>"
    elif "Nyx" in item:
        return "<:Nyx:1438190327893721139>"
    elif "Oberon" in item:
        return "<:Oberon:1438190330326286416>"
    elif "Octavia" in item:
        return "<:Octavia:1438190332100481257>"
    elif "Oraxia" in item:
        return "<:Oraxia:1438190333841117309>"
    elif "Protea" in item:
        return "<:Protea:1438190335426826291>"
    elif "Qorvex" in item:
        return "<:Qorvex:1438190336718405795>"
    elif "Revenant" in item:
        return "<:Revenant:1438190338828144670>"
    elif "Rhino" in item:
        return "<:Rhino:1438190340438753300>"
    elif "Saryn" in item:
        return "<:Saryn:1438190342066278490>"
    elif "Sevagoth" in item:
        return "<:Sevagoth:1438190343605452942>"
    elif "Styanax" in item:
        return "<:Styanax:1438190345077915688>"
    elif "Temple" in item:
        return "<:Temple:1438190346789060828>"
    elif "Titania" in item:
        return "<:Titania:1438190348584226919>"
    elif "Trinity" in item:
        return "<:Trinity:1438190350215676076>"
    elif "Valkyr" in item:
        return "<:Valkyr:1438190352224751686>"
    elif "Vauban" in item:
        return "<:Vauban:1438190353558536242>"
    elif "Volt" in item:
        return "<:Volt:1438190355274141899>"
    elif "Voruna" in item:
        return "<:Voruna:1438190356872302643>"
    elif "Wisp" in item:
        return "<:Wisp:1438190358394703973>"
    elif "Wukong" in item:
        return "<:Wukong:1438190359879614535>"
    elif "Xaku" in item:
        return "<:Xaku:1438190361561534645>"
    elif "Yareli" in item:
        return "<:Yareli:1438190363104772187>"
    elif "Zephyr" in item:
        return "<:Zephyr:1438190364665315529>"

    # incarnon genesis
    elif "Ack & Brunt" in item:
        return "<:AckBrunt:1438194050720333997>"
    elif "Angstrum" in item:
        return "<:Angstrum:1438194052251127909>"
    elif "Anku" in item:
        return "<:Anku:1438194053656084644>"
    elif "Atomos" in item:
        return "<:Atomos:1438194055216631970>"
    elif "Bo" in item:
        return "<:Bo:1438194056911126639>"
    elif "Boar" in item:
        return "<:Boar:1438194058324476045>"
    elif "Boltor" in item:
        return "<:Boltor:1438194060132089908>"
    elif "Braton" in item:
        return "<:Braton:1438194061788844033>"
    elif "Bronco" in item:
        return "<:Bronco:1438194063546515587>"
    elif "Burston" in item:
        return "<:Burston:1438194065136160859>"
    elif "Ceramic Dagger" in item:
        return "<:CeramicDagger:1438194066679529583>"
    elif "Cestra" in item:
        return "<:Cestra:1438194068051198112>"
    elif "Dera" in item:
        return "<:Dera:1438194069775057118>"
    elif "Despair" in item:
        return "<:Despair:1438194071360372756>"
    elif "Dread" in item:
        return "<:Dread:1438194073117917194>"
    elif "Dual Ichor" in item:
        return "<:DualIchor:1438194074753700032>"
    elif "Dual Toxocyst" in item:
        return "<:DualToxocyst:1438194076171243710>"
    elif "Furax" in item:
        return "<:Furax:1438194077781721231>"
    elif "Furis" in item:
        return "<:Furis:1438194079279222814>"
    elif "Gammacor" in item:
        return "<:Gammacor:1438194080722190426>"
    elif "Gorgon" in item:
        return "<:Gorgon:1438194112707825824>"
    elif "Hate" in item:
        return "<:Hate:1438194114070839458>"
    elif "Kunai" in item:
        return "<:Kunai:1438194115337654422>"
    elif "Lato" in item:
        return "<:Lato:1438194117032017950>"
    elif "Latron" in item:
        return "<:Latron:1438194118802018334>"
    elif "Lex" in item:
        return "<:Lex:1438194120513556573>"
    elif "Magistar" in item:
        return "<:Magistar:1438194121952202763>"
    elif "Miter" in item:
        return "<:Miter:1438194123843567696>"
    elif "Nami Solo" in item:
        return "<:NamiSolo:1438194125559300107>"
    elif "Okina" in item:
        return "<:Okina:1438194127257993338>"
    elif "Paris" in item:
        return "<:Paris:1438194128927064124>"
    elif "Sibear" in item:
        return "<:Sibear:1438194130324029495>"
    elif "Sicarus" in item:
        return "<:Sicarus:1438194132077252609>"
    elif "Skana" in item:
        return "<:Skana:1438194133641728123>"
    elif "Soma" in item:
        return "<:Soma:1438194135449342053>"
    elif "Strun" in item:
        return "<:Strun:1438194137127190669>"
    elif "Sybaris" in item:
        return "<:Sybaris:1438194138905575624>"
    elif "Torid" in item:
        return "<:Torid:1438194140486701189>"
    elif "Vasto" in item:
        return "<:Vasto:1438194142156161034>"
    elif "Zylok" in item:
        return "<:Zylok:1438194143531630796>"

    else:
        return ""
