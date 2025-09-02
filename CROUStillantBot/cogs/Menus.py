import pytz
import discord
import traceback

from ..utils.functions import getCrousLink, createOption, getClockEmoji
from ..utils.date import getCleanDate
from ..utils.views import MenuView
from discord.ext import commands, tasks
from datetime import datetime, time


class Menus(commands.Cog):
    """
    Rafraîchissement des menus
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client

        self.task.start()

    def cog_unload(self) -> None:
        """
        Arrête la tâche lorsque le module est déchargé.
        """
        self.task.cancel()

    def cog_reload(self) -> None:
        """
        Arrête la tâche lorsque le module est rechargé.
        """
        self.task.cancel()

    @tasks.loop(time=[time(hour=h, minute=0) for h in range(0, 24)])
    async def task(self) -> None:
        """
        Rafraîchit les menus.
        """
        try:
            print("Rafraîchissement des menus...")

            now = datetime.now(tz=pytz.timezone("Europe/Paris"))
            emoji = getClockEmoji(now)

            settings = await self.client.entities.parametres.getAll()

            for setting in settings:
                guild = self.client.get_guild(setting.get("guild_id"))

                if not guild:
                    await self.client.entities.parametres.delete(
                        setting.get("guild_id"), setting.get("rid")
                    )
                    await self.client.entities.logs.insert(
                        setting.get("guild_id"),
                        self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                        f"Le serveur {setting.get('guild_id')} n'existe plus",
                    )
                    continue

                print(
                    f"Rafraîchissement du menu pour {setting.get('guild_id')} - {setting.get('channel_id')} ({setting.get('rid')})"
                )

                try:
                    channel = guild.get_channel(setting.get("channel_id"))
                except discord.NotFound:
                    await self.client.entities.parametres.delete(
                        setting.get("guild_id"), setting.get("rid")
                    )
                    await self.client.entities.logs.insert(
                        setting.get("guild_id"),
                        self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                        f"Le salon {setting.get('channel_id')} n'existe plus",
                    )
                    continue
                except discord.RateLimited or discord.DiscordServerError:
                    continue
                except discord.Forbidden:
                    await self.client.entities.parametres.delete(
                        setting.get("guild_id"), setting.get("rid")
                    )
                    await self.client.entities.logs.insert(
                        setting.get("guild_id"),
                        self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                        f"Impossible de récupérer le salon {setting.get('channel_id')}",
                    )
                    continue
                except Exception:
                    print(
                        f"Impossible de récupérer le salon {setting.get('channel_id')} pour {setting.get('guild_id')}"
                    )
                    print(traceback.format_exc())
                    await self.client.entities.logs.insert(
                        setting.get("guild_id"),
                        self.client.entities.logs.ERREUR_INCONNUE,
                        f"Une erreur est survenue lors de la récupération du salon {setting.get('channel_id')}. Nous vous prions de nous excuser pour la gêne occasionnée.",
                    )
                    continue

                if not channel:
                    await self.client.entities.parametres.delete(
                        setting.get("guild_id"), setting.get("rid")
                    )
                    await self.client.entities.logs.insert(
                        setting.get("guild_id"),
                        self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                        f"Le salon {setting.get('channel_id')} n'existe plus",
                    )
                    continue

                restaurant = await self.client.cache.restaurants.getFromId(
                    setting.get("rid")
                )
                menus = await self.client.entities.menus.getCurrent(
                    id=setting.get("rid"), date=now
                )

                options = []

                exist = False
                for menu in menus:
                    if menu.get("date").strftime("%d-%m-%Y") == now.strftime(
                        "%d-%m-%Y"
                    ):
                        exist = True
                        break

                if not exist:
                    m_saved = None
                    options.append(createOption(restaurant, None, default=True))
                else:
                    m_saved = menu
                    options.append(createOption(restaurant, menu, default=True))

                for menu in menus:
                    if menu.get("date") > now.date() and len(options) < 25:
                        options.append(createOption(restaurant, menu))

                timestamp = int(now.timestamp())
                content = f"{emoji} **Mis à jour <t:{timestamp}:R> (<t:{timestamp}>)**"

                view = MenuView(
                    restaurant=restaurant,
                    menu=m_saved,
                    menus=menus,
                    options=options,
                    map=f"https://www.google.fr/maps/dir/{restaurant.get('latitude')},{restaurant.get('longitude')}/@{restaurant.get('latitude')},{restaurant.get('longitude')},18.04",
                    link=getCrousLink(restaurant),
                )

                embed = discord.Embed(
                    title=f"Menu du **`{getCleanDate(now)}`** - {setting.get('repas').title()}",
                    color=self.client.colour,
                )
                embed.set_image(
                    url=f"https://api.croustillant.menu/v1/restaurants/{restaurant.get('rid')}/menu/{now.strftime('%d-%m-%Y')}/image?theme={setting.get('theme')}&repas={setting.get('repas')}&timestamp={timestamp}"
                )
                embed.set_footer(
                    text=self.client.footer_text, icon_url=self.client.avatar_url
                )

                if not setting.get("message_id"):
                    try:
                        message = await channel.send(
                            content=content, embed=embed, view=view
                        )
                        await self.client.entities.parametres.update(
                            id=setting.get("guild_id"),
                            channel_id=setting.get("channel_id"),
                            message_id=message.id,
                            rid=setting.get("rid"),
                            theme=setting.get("theme"),
                            repas=setting.get("repas"),
                        )
                    except discord.RateLimited or discord.DiscordServerError:
                        continue
                    except discord.Forbidden or discord.NotFound:
                        await self.client.entities.parametres.delete(
                            setting.get("guild_id"), setting.get("rid")
                        )
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                            f"Impossible d'envoyer l'image pour {setting.get('guild_id')} ({setting.get('rid')})",
                        )
                        continue
                    except Exception:
                        print(
                            f"Impossible d'envoyer l'image pour {setting.get('guild_id')} ({setting.get('rid')})"
                        )
                        print(traceback.format_exc())
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.ERREUR_INCONNUE,
                            f"Une erreur est survenue lors de l'envoi de l'image pour {setting.get('guild_id')} ({setting.get('rid')}). Nous vous prions de nous excuser pour la gêne occasionnée.",
                        )
                        continue
                    else:
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.MENU_AJOUTE,
                            f"Menu mis à jour pour {setting.get('rid')}",
                        )
                else:
                    try:
                        message = await channel.fetch_message(setting.get("message_id"))
                        await message.edit(content=content, embed=embed, view=view)
                    except discord.NotFound:
                        await self.client.entities.parametres.delete(
                            setting.get("guild_id"), setting.get("rid")
                        )
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                            f"Impossible de récupérer le message {setting.get('message_id')} pour {setting.get('guild_id')} ({setting.get('rid')})",
                        )
                        continue
                    except discord.RateLimited or discord.DiscordServerError:
                        continue
                    except discord.Forbidden:
                        await self.client.entities.parametres.delete(
                            setting.get("guild_id"), setting.get("rid")
                        )
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                            f"Impossible d'éditer l'image pour {setting.get('guild_id')} ({setting.get('rid')})",
                        )
                        continue
                    except Exception:
                        print(
                            f"Impossible d'éditer l'image pour {setting.get('guild_id')} - {setting.get('message_id')} ({setting.get('rid')})"
                        )
                        print(traceback.format_exc())
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.ERREUR_INCONNUE,
                            f"Une erreur est survenue lors de l'édition de l'image pour {setting.get('guild_id')} - {setting.get('message_id')} ({setting.get('rid')}). Nous vous prions de nous excuser pour la gêne occasionnée.",
                        )
                    else:
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.MENU_MIS_A_JOUR,
                            f"Menu mis à jour pour {setting.get('rid')}",
                        )
        except Exception as e:
            print(f"Une erreur est survenue: {e}")
            print(traceback.format_exc())

    @task.before_loop
    async def wait_until_ready(self):
        print("[Menus] CROUStillant n'est pas encore en ligne...")

        # Attends que le bot soit prêt
        await self.client.wait_until_ready()

        print("[Menus] CROUStillant est désormais en ligne !")

        hour = self.task.time[1].hour - self.task.time[0].hour
        minute = self.task.time[0].minute
        print(f"Tâche s'exécutant toutes les {hour} heures et {minute} minutes")

        await self.task()


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Menus(client))
