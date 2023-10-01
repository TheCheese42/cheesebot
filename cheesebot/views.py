import discord


class LinkView(discord.ui.View):
    def __init__(self, url: str, text: str):
        super().__init__()
        self.add_item(discord.ui.Button(label=text, url=url))


class MultiLinkView(discord.ui.View):
    def __init__(
        self,
        urls: tuple[str, ...],
        texts: tuple[str, ...],
    ):
        super().__init__()
        if len(urls) != len(texts):
            raise ValueError("Provided arguments should have same length.")
        for url, text in zip(urls, texts):
            self.add_item(discord.ui.Button(label=text, url=url))
