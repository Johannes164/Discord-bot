import discord
from discord.ext import commands
from bible_api import get_random_verse
from datetime import datetime

def has_required_role(interaction: discord.Interaction, roles: list[int]) -> bool:
    """
    Sjekker om brukeren har minst én av rollene i listen 'roles'.
    """
    user_role_ids = [role.id for role in interaction.user.roles]
    return any(role_id in user_role_ids for role_id in roles)

class BibleCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ------------------------------------------------
    # 1) /dagens
    # ------------------------------------------------
    @discord.app_commands.command(
        name="dagens",
        description="Sender et tilfeldig bibelvers i #1333513186938327211"
    )
    async def send_random_verse(self, interaction: discord.Interaction):
        await interaction.response.defer()

        print("Henter tilfeldig bibelvers...")
        random_verse = get_random_verse()
        print("Tilfeldig vers hentet! Oppretter embed...")
        
        embed = discord.Embed(
            title="Dagens Bibelvers",
            colour=0xd8c964,
            timestamp=datetime.now()
        )
        embed.set_author(
            name="Biblica® Open",
            url="https://ebible.org/noblb/",
            icon_url="https://upload.wikimedia.org/wikipedia/en/b/b2/Biblica_Logo_for_Public_Web_Use.png"
        )
        embed.add_field(
            name=random_verse['reference'],
            value=f"> {random_verse['content']}",
            inline=False
        )
        embed.set_thumbnail(url="https://i0.wp.com/www.cruciformcoc.com/wp-content/uploads/2019/05/Cross.jpg?resize=400%2C400&ssl=1")
        embed.set_footer(text="En Levende Bok: Det Nye Testamentet")

        print("Embed opprettet! Sender til #1333513186938327211...")
        channel = self.bot.get_channel(1333513186938327211)
        if channel:
            await channel.send(embed=embed)
            await interaction.followup.send("Bibelverset er sendt!", ephemeral=True)
        else:
            await interaction.followup.send("Finner ikke kanalen!", ephemeral=True)

    # ------------------------------------------------
    # 2) /send_embed_multi – kan utelate beskrivelse, opptil 10 felter
    # ------------------------------------------------
    @discord.app_commands.command(
        name="send_embed_multi",
        description="Sender en embed i en spesifisert kanal (hvis du har riktig rolle)."
    )
    @discord.app_commands.check(
        lambda i: has_required_role(
            i,
            [1333496666006749225, 1333497052528902144]
        )
    )
    async def send_embed_multi(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str,
        
        description: str = None,
        # Hvor mange felter ønsker du å fylle ut (1–10)?
        number_of_fields: int = 1,
        
        field_title_1: str = None,
        field_value_1: str = None,
        
        field_title_2: str = None,
        field_value_2: str = None,
        
        field_title_3: str = None,
        field_value_3: str = None,
        
        field_title_4: str = None,
        field_value_4: str = None,
        
        field_title_5: str = None,
        field_value_5: str = None,
        
        field_title_6: str = None,
        field_value_6: str = None,
        
        field_title_7: str = None,
        field_value_7: str = None,
        
        field_title_8: str = None,
        field_value_8: str = None,
        
        field_title_9: str = None,
        field_value_9: str = None,
        
        field_title_10: str = None,
        field_value_10: str = None
    ):

        await interaction.response.defer()

        # Opprett embed
        embed = discord.Embed(
            title=title,
            description=description if description else "",  # tom streng om None
            colour=0xd8c964
        )

        # Pakk tittel/verdi i en liste for enkel looping
        field_info = [
            (field_title_1, field_value_1),
            (field_title_2, field_value_2),
            (field_title_3, field_value_3),
            (field_title_4, field_value_4),
            (field_title_5, field_value_5),
            (field_title_6, field_value_6),
            (field_title_7, field_value_7),
            (field_title_8, field_value_8),
            (field_title_9, field_value_9),
            (field_title_10, field_value_10),
        ]

        # Legg til felter i henhold til number_of_fields
        for i in range(min(number_of_fields, 10)):
            f_title, f_value = field_info[i]
            # Hvis begge er None eller tomme, hopper vi over
            if not f_title and not f_value:
                continue
            
            # Sett noen standardverdier om man bare fylte inn f.eks. tittel
            title_str = f_title if f_title else f"Felt {i+1}"
            value_str = f_value if f_value else "Ingen verdi oppgitt"

            embed.add_field(
                name=title_str,
                value=value_str,
                inline=False
            )

        # Send til spesifisert kanal
        await channel.send(embed=embed)
        await interaction.followup.send("Embed sendt!", ephemeral=True)

    # Feilhåndtering – hvis brukeren mangler rolle eller noe går galt
    @send_embed_multi.error
    async def send_embed_multi_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.AppCommandError):
            await interaction.response.send_message(
                "Beklager, du har ikke riktig rolle eller har oppgitt ugyldige argumenter.",
                ephemeral=True
            )

# Setup-funksjon for cogen
async def setup(bot: commands.Bot):
    await bot.add_cog(BibleCommands(bot))
