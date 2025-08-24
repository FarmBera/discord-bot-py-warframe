def get_emoji(item: str):
    item = item.lower()

    # 7; general items
    if "riven" in item:
        return "<:rivenmod:1407864916492288070>"
    elif "kuva" in item:
        return "<:kuva:1407864912839049269>"
    elif "endo" in item:
        return "<:endo:1407864907235463319>"
    elif "arcane enhancements" in item:
        return "<:ArcaneEnhance:1407880465146314785>"
    elif "reactor" in item:
        return "<:OrokinReactor:1407882689331335188>"
    elif "catalyst" in item:
        return "<:OrokinCatalyst:1407882687032852551>"
    elif "ducat" in item:
        return "<:ducats:1408813306415808676>"
    elif "credit" in item:
        return "<:credits:1408813303798563077>"
    # 2; forma
    elif "forma" in item:
        return "<:forma:1407864910997622916>"
    elif "aura forma" in item:
        return "<:auraforma:1407864904404172850>"

    # 5; adapter
    elif "exilus weapon" in item:
        return "<:ExilusWeaponAdapter:1407881645784305759>"
    elif "exilus warframe" in item:
        return "<:ExilusWarframeAdapter:1407881644022435961>"
    elif "primary arcane" in item:
        return "<:PrimaryArcaneAdapter:1407881651727368302>"
    elif "secondary arcane" in item:
        return "<:SecondaryArcaneAdapter:1407881654424567869>"
    elif "melee arcane" in item:
        return "<:MeleeArcaneAdapter:1407881648825045135>"

    # 6; shard
    elif "crimson" in item:
        return "<:CrimsonArchonShard:1407864644923691028>"
    elif "azure" in item:
        return "<:AzureArchonShard:1407864641714913384>"
    elif "amber" in item:
        return "<:AmberArchonShard:1407864636698529924>"
    elif "emerald" in item:
        return "<:EmeraldArchonShard:1407864648409026580>"
    elif "topaz" in item:
        return "<:TopazArchonShard:1407864650510372918>"
    elif "violet" in item:
        return "<:VioletArchonShard:1407864652175642665>"

    # 5; void relics
    elif "axi" in item:
        return "<:AxiRelic:1408056877992116355>"
    elif "lith" in item:
        return "<:LithRelic:1408056882051944489>"
    elif "meso" in item:
        return "<:MesoRelic:1408056873747484713>"
    elif "neo" in item:
        return "<:NeoRelic:1408056875735584818>"
    elif "requiem" in item:
        return "<:RequiemRelic:1408056880206577705>"

    # 5; 3 day boosters
    elif "affinity" in item:
        return "<:3DayAffinity:1407881490381013034>"
    elif "mod" in item:
        return "<:3DayModDropChance:1407881495023980704>"
    elif "credit" in item:
        return "<:3DayCredit:1407881492553531432>"
    elif "resource drop" in item:
        return "<:3DayResourceDropChance:1407881500409466942>"
    elif "resource" in item:
        return "<:3DayResource:1407881497976901773>"

    else:
        return ""
