from discord.ui import View, Button

from src.translator import ts
from config.TOKEN import HOMEPAGE, DONATION

pf: str = "view.support-"


class SupportView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(label=ts.get(f"{pf}help"), url=f"{HOMEPAGE}"))
        self.add_item(Button(label=ts.get(f"{pf}tos"), url=f"{HOMEPAGE}?id=tos"))
        self.add_item(
            Button(label=ts.get(f"{pf}privacy"), url=f"{HOMEPAGE}/?id=privacy")
        )
        self.add_item(Button(label=ts.get(f"{pf}donate"), url=DONATION, row=1))
