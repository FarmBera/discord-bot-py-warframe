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

    else:
        return ""
