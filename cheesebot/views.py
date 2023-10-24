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


class TextResponseButtonView(discord.ui.View):
    def __init__(
        self,
        label: str,
        response_text: str,
        style: discord.ButtonStyle = discord.ButtonStyle.primary,
        timeout: int = 180,
    ):
        super().__init__(timeout=timeout, disable_on_timeout=True)
        button: discord.ui.Button = discord.ui.Button(
            style=style,
            label=label,
        )

        async def callback(inter: discord.Interaction):
            await inter.respond(response_text)

        button.callback = callback  # type: ignore
        self.add_item(button)
