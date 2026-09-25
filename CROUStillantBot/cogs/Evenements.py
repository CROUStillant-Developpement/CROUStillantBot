import asyncio
import json
import traceback

from datetime import datetime
from os import environ

import aiohttp
import pytz

from discord.ext import commands

# URL de l'API CROUStillant (flux des événements : GET /v1/evenements)
API_URL = environ.get("API_URL", "https://api.croustillant.menu").rstrip("/")

# User-Agent envoyé à l'API (obligatoire)
USER_AGENT = "CROUStillantBot/3.0.0 (+https://croustillant.menu; croustillant@bayfield.dev)"

# L'API envoie un commentaire toutes les 15 secondes : sans données pendant ce délai, la connexion est
# considérée comme perdue
READ_TIMEOUT = 45

# Délais de reconnexion (secondes)
RECONNECT_DELAY = 5
RECONNECT_DELAY_MAX = 60

# Délai de regroupement des événements avant rafraîchissement (secondes) : un restaurant dont plusieurs
# menus changent en même temps n'est rafraîchi qu'une seule fois
DEBOUNCE_DELAY = 5


class Evenements(commands.Cog):
    """
    Abonnement au flux des événements en temps réel de l'API.

    Les messages des menus sont rafraîchis dès qu'un menu change, sans attendre la tâche horaire (qui reste
    active en secours).
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client

        self.connected = False
        self.last_event_id: int | None = None
        self.received = 0
        self.reconnect_delay = RECONNECT_DELAY

        self.pending_restaurants: set[int] = set()
        self.pending_cache = False

        self._task: asyncio.Task | None = None
        self._flush_task: asyncio.Task | None = None

    async def cog_load(self) -> None:
        """
        Démarre l'abonnement lorsque le module est chargé.
        """
        self._task = asyncio.create_task(self.run())

    async def cog_unload(self) -> None:
        """
        Arrête l'abonnement lorsque le module est déchargé.
        """
        for task in (self._task, self._flush_task):
            if task and not task.done():
                task.cancel()

    @property
    def status(self) -> dict:
        """
        État de l'abonnement (exposé par l'API de statut).
        """
        return {
            "connected": self.connected,
            "last_event_id": self.last_event_id,
            "received": self.received,
        }

    async def run(self) -> None:
        """
        Maintient la connexion au flux des événements, et se reconnecte en cas de coupure.
        """
        await self.client.wait_until_ready()

        while True:
            try:
                await self.listen()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f"[Evenements] Connexion au flux perdue ({type(e).__name__}: {e})")
            finally:
                self.connected = False

            print(f"[Evenements] Reconnexion dans {self.reconnect_delay} secondes...")
            await asyncio.sleep(self.reconnect_delay)
            self.reconnect_delay = min(self.reconnect_delay * 2, RECONNECT_DELAY_MAX)

    async def listen(self) -> None:
        """
        Se connecte au flux et traite les événements jusqu'à la fin de la connexion.
        """
        headers = {"User-Agent": USER_AGENT, "Accept": "text/event-stream"}
        if self.last_event_id is not None:
            # Reçoit d'abord les événements manqués pendant la coupure
            headers["Last-Event-ID"] = str(self.last_event_id)

        async with self.client.session.get(
            f"{API_URL}/v1/evenements",
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=None, sock_connect=10, sock_read=READ_TIMEOUT),
        ) as response:
            if response.status != 200:
                raise ConnectionError(f"HTTP {response.status}")

            self.connected = True
            self.reconnect_delay = RECONNECT_DELAY
            print(f"[Evenements] Connecté au flux {API_URL}/v1/evenements (dernier événement : {self.last_event_id})")

            event_id, data = None, []

            async for raw in response.content:
                line = raw.decode("utf-8").rstrip("\r\n")

                if line == "":
                    # Fin d'un événement
                    if data:
                        self.handle(event_id, "\n".join(data))
                    event_id, data = None, []
                elif line.startswith(":"):
                    # Commentaire (maintien de la connexion)
                    continue
                else:
                    field, _, value = line.partition(":")
                    value = value.removeprefix(" ")

                    if field == "id":
                        event_id = value
                    elif field == "data":
                        data.append(value)
                    elif field == "retry" and value.isdigit():
                        self.reconnect_delay = max(RECONNECT_DELAY, int(value) // 1000)

        raise ConnectionError("Flux terminé par le serveur")

    def handle(self, event_id: str | None, data: str) -> None:
        """
        Traite un événement reçu.

        :param event_id: L'ID de l'événement
        :type event_id: str | None
        :param data: Les données de l'événement (JSON)
        :type data: str
        """
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            print(f"[Evenements] Événement illisible ignoré : {data[:200]}")
            return

        if event_id and event_id.isdigit():
            self.last_event_id = int(event_id)
        self.received += 1

        event_type: str = event.get("type", "")
        rid = event.get("code")

        if event_type.startswith("restaurant."):
            # Nom, état... : le cache des restaurants est rechargé
            self.pending_cache = True
            if rid is not None and event_type != "restaurant.created":
                self.pending_restaurants.add(rid)
        elif event_type.startswith("menu.") and rid is not None:
            # Les menus passés ne sont plus affichés
            date = event.get("date")
            today = datetime.now(tz=pytz.timezone("Europe/Paris")).date()
            if date and datetime.strptime(date, "%d-%m-%Y").date() < today:
                return

            self.pending_restaurants.add(rid)
        else:
            return

        if self._flush_task is None or self._flush_task.done():
            self._flush_task = asyncio.create_task(self.flush())

    async def flush(self) -> None:
        """
        Rafraîchit les restaurants concernés par les événements reçus pendant le délai de regroupement.

        Les événements reçus pendant un rafraîchissement sont traités au tour suivant.
        """
        while self.pending_restaurants or self.pending_cache:
            await asyncio.sleep(DEBOUNCE_DELAY)

            restaurants, self.pending_restaurants = self.pending_restaurants, set()
            reload_cache, self.pending_cache = self.pending_cache, False

            try:
                if reload_cache:
                    await self.client.cache.restaurants.load()

                menus = self.client.get_cog("Menus")
                if restaurants and menus is not None:
                    print(f"[Evenements] Rafraîchissement de {len(restaurants)} restaurant(s) : {sorted(restaurants)}")
                    await menus.refresh_restaurants(restaurants)
            except Exception:
                print("[Evenements] Erreur lors du rafraîchissement")
                print(traceback.format_exc())


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Evenements(client))
