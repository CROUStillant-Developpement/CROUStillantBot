import traceback

from datetime import datetime, time

import discord
import pytz

from discord.ext import commands, tasks

from ..utils.functions import create_option
from ..views.menu import MenuTaskView


class Menus(commands.Cog):
    """
    Rafraîchissement des menus.
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

    async def get_menu(self, restaurant: dict, menu: dict) -> str:
        """
        Récupère le menu formaté en texte.

        :param restaurant: Le restaurant.
        :type restaurant: dict
        :param menu: Le menu.
        :type menu: dict
        :return: Le menu formaté en texte.
        :rtype: str
        """
        menu_from_date = await self.client.entities.menus.get_from_date(id=restaurant.get("rid"), date=menu.get("date"))

        menu_per_day = {}
        for row in menu_from_date:
            date = row.get("date").strftime("%d-%m-%Y")

            day_menu = menu_per_day.setdefault(date, {"code": row.get("mid"), "date": date, "repas": []})

            repas_list = day_menu["repas"]

            if not repas_list or row.get("tpr") not in repas_list[-1]["type"]:
                repas_list.append(
                    {
                        "code": row.get("rpid"),
                        "type": row.get("tpr"),
                        "categories": [],
                    }
                )

            repas = repas_list[-1]
            categories_list = repas["categories"]

            if not categories_list or row.get("tpcat") not in categories_list[-1]["libelle"]:
                categories_list.append(
                    {
                        "code": row.get("catid"),
                        "libelle": row.get("tpcat"),
                        "ordre": row.get("cat_ordre") + 1,
                        "plats": [],
                    }
                )

            categories_list[-1]["plats"].append(
                {
                    "code": row.get("platid"),
                    "ordre": row.get("plat_ordre") + 1,
                    "libelle": row.get("plat"),
                }
            )

        content = "# Menu\n\n"

        for meal in menu_per_day[menu.get("date").strftime("%d-%m-%Y")].get("repas"):
            count = 0
            for category in meal.get("categories"):
                text = ""

                for dish in category.get("plats"):
                    if not dish.get("libelle") == "":
                        text += f"• {dish.get('libelle')}\n"

                content += f"### {category.get('libelle')}\n{text}\n"
                count += 1

                if len(meal.get("categories")) > 25 and count == 24:
                    content += f"Et {len(meal.get('categories')) - count} autres categories\n"
                    break

            break

        return content

    @tasks.loop(time=[time(hour=h, minute=0) for h in range(0, 24)])
    async def task(self) -> None:
        """
        Rafraîchit les menus.
        """
        try:
            print("Rafraîchissement des menus...")

            now = datetime.now(tz=pytz.timezone("Europe/Paris"))

            if self.client.env == "dev":
                settings = []
                settings = [
                    {
                        "guild_id": 1042162372527271947,
                        "channel_id": 1166644928898666547,
                        "message_id": None,
                        "rid": 871,
                        "theme": "light",
                        "repas": "midi",
                    }
                ]
            else:
                settings = await self.client.entities.parametres.get_all()

            for setting in settings:
                guild = self.client.get_guild(setting.get("guild_id"))

                if not guild:
                    await self.client.entities.parametres.delete(setting.get("guild_id"), setting.get("rid"))
                    await self.client.entities.logs.insert(
                        setting.get("guild_id"),
                        self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                        f"Le serveur {setting.get('guild_id')} n'existe plus",
                    )
                    continue

                print(
                    f"Rafraîchissement du menu pour {setting.get('guild_id')} - {setting.get('channel_id')} \
({setting.get('rid')})"
                )

                try:
                    channel = guild.get_channel(setting.get("channel_id"))
                except discord.NotFound:
                    await self.client.entities.parametres.delete(setting.get("guild_id"), setting.get("rid"))
                    await self.client.entities.logs.insert(
                        setting.get("guild_id"),
                        self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                        f"Le salon {setting.get('channel_id')} n'existe plus",
                    )
                    continue
                except discord.RateLimited or discord.DiscordServerError:
                    continue
                except discord.Forbidden:
                    await self.client.entities.parametres.delete(setting.get("guild_id"), setting.get("rid"))
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
                        f"Une erreur est survenue lors de la récupération du salon {setting.get('channel_id')}. Nous \
vous prions de nous excuser pour la gêne occasionnée.",
                    )
                    continue

                if not channel:
                    await self.client.entities.parametres.delete(setting.get("guild_id"), setting.get("rid"))
                    await self.client.entities.logs.insert(
                        setting.get("guild_id"),
                        self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                        f"Le salon {setting.get('channel_id')} n'existe plus",
                    )
                    continue

                restaurant = await self.client.cache.restaurants.get_from_id(setting.get("rid"))
                menus = await self.client.entities.menus.get_current(id=setting.get("rid"), date=now)

                options = []
                added_dates = []

                exist = False
                for menu in menus:
                    if menu.get("date").strftime("%d-%m-%Y") == now.strftime("%d-%m-%Y"):
                        exist = True
                        break

                if not exist:
                    m_saved = None
                    options.append(create_option(restaurant, None, default=True))
                else:
                    m_saved = menu
                    options.append(create_option(restaurant, menu, default=True))
                    added_dates.append(menu.get("date").strftime("%d-%m-%Y"))

                for menu in menus:
                    if menu.get("date") > now.date() and len(options) < 25:
                        if menu.get("date").strftime("%d-%m-%Y") in added_dates:
                            continue

                        options.append(create_option(restaurant, menu))
                        added_dates.append(menu.get("date").strftime("%d-%m-%Y"))

                view = MenuTaskView(
                    restaurant=restaurant,
                    menu=await self.get_menu(restaurant, m_saved)
                    if m_saved
                    else "Aucun menu disponible pour cette date.",
                    get_menu=self.get_menu,
                    menus=menus,
                    theme=setting.get("theme"),
                    repas=setting.get("repas"),
                    options=options,
                    client=self.client,
                )

                if not setting.get("message_id"):
                    try:
                        message = await channel.send(view=view)

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
                        await self.client.entities.parametres.delete(setting.get("guild_id"), setting.get("rid"))
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                            f"Impossible d'envoyer l'image pour {setting.get('guild_id')} ({setting.get('rid')})",
                        )
                        continue
                    except Exception:
                        print(f"Impossible d'envoyer l'image pour {setting.get('guild_id')} ({setting.get('rid')})")
                        print(traceback.format_exc())
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.ERREUR_INCONNUE,
                            f"Une erreur est survenue lors de l'envoi de l'image pour {setting.get('guild_id')} \
({setting.get('rid')}). Nous vous prions de nous excuser pour la gêne occasionnée.",
                        )
                        continue
                    else:
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.MENU_AJOUTE,
                            f"Menu envoyé pour {setting.get('rid')}",
                        )
                else:
                    try:
                        message = await channel.fetch_message(setting.get("message_id"))
                        await message.edit(view=view)
                    except discord.NotFound:
                        await self.client.entities.parametres.delete(setting.get("guild_id"), setting.get("rid"))
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                            f"Impossible de récupérer le message {setting.get('message_id')} pour \
                                {setting.get('guild_id')} ({setting.get('rid')})",
                        )
                        continue
                    except discord.RateLimited or discord.DiscordServerError:
                        continue
                    except discord.Forbidden:
                        await self.client.entities.parametres.delete(setting.get("guild_id"), setting.get("rid"))
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.SUPPRESSION_AUTOMATIQUE,
                            f"Impossible d'éditer l'image pour {setting.get('guild_id')} ({setting.get('rid')})",
                        )
                        continue
                    except Exception:
                        print(
                            f"Impossible d'éditer l'image pour {setting.get('guild_id')} - {setting.get('message_id')} \
({setting.get('rid')})"
                        )
                        print(traceback.format_exc())
                        await self.client.entities.logs.insert(
                            setting.get("guild_id"),
                            self.client.entities.logs.ERREUR_INCONNUE,
                            f"Une erreur est survenue lors de l'édition de l'image pour {setting.get('guild_id')} - \
{setting.get('message_id')} ({setting.get('rid')}). Nous vous prions de nous excuser pour la gêne occasionnée.",
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
    async def wait_until_ready(self) -> None:
        """
        Attends que le bot soit prêt avant de démarrer la tâche.
        """
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
