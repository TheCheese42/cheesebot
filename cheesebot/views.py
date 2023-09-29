import discord


class LinkView(discord.ui.View):
    def __init__(self, url: str, text: str):
        super().__init__()
        self.add_item(discord.ui.Button(label=text, url=url))
