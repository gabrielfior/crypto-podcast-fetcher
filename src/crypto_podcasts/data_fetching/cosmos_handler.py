from azure.cosmos import CosmosClient as AzureCosmosClient
from azure.cosmos.container import ContainerProxy

from src.crypto_podcasts.config import DBConfig
from src.crypto_podcasts.data_fetching.models import PodcastEpisode


class CosmosClient:
    def __init__(self, db_config: DBConfig):
        self.db_config = db_config
        client = AzureCosmosClient(
            db_config.COSMOS_URI, db_config.COSMOS_DB_ACCOUNT_KEY
        )
        db = client.create_database_if_not_exists(db_config.COSMOS_DB_NAME)
        self.container_client: ContainerProxy = db.get_container_client(
            db_config.COSMOS_CONTAINER_NAME
        )

    def get_episode(self, uuid: str) -> list[PodcastEpisode]:
        items = list(
            self.container_client.query_items(
                query=f"Select * from episodes r where r.uuid='{uuid}'",
                enable_cross_partition_query=True,
            )
        )
        return [PodcastEpisode.model_validate(i) for i in items]

    def fetch_existing_uuids(self):
        return [e["uuid"] for e in self.container_client.read_all_items()]

    def store_episode_if_not_exists(self, episode: PodcastEpisode) -> None:
        existing_uuids = self.fetch_existing_uuids()
        if episode.uuid in existing_uuids:
            print(f"Episode {episode.uuid} already exists. Skipping.")
            return
        print(f"Storing episode {episode.uuid}")
        self.container_client.upsert_item(episode.dict())

    def insert_episode_prediction(
        self, uuid: str, prediction_id: str, prediction_status: str
    ):
        # Check that episode exists - if not, raise Error
        # fetch episode, add transcript as key, upsert
        episodes = self.get_episode(uuid)
        if not episodes:
            raise ValueError(f"Episode with uuid {uuid} does not exist")
        episode = episodes[0]
        if episode.prediction_id is not None:
            print("Episode prediction_id available. Skipping.")
            return
        episode.prediction_id = prediction_id
        episode.prediction_status = prediction_status
        self.container_client.upsert_item(episode.dict())

    def insert_episode_transcript(self, uuid: str, transcript: str):
        # Check that episode exists - if not, raise Error
        # fetch episode, add transcript as key, upsert
        episodes = self.get_episode(uuid)
        if not episodes:
            raise ValueError(f"Episode with uuid {uuid} does not exist")
        episode = episodes[0]
        if episode.transcript is not None:
            print("Episode transcript already available. Skipping.")
            return
        episode.transcript = transcript
        self.container_client.upsert_item(episode.dict())

    # ToDo - Consider using SQLAlchemy instead of writing queries by hand.
    def fetch_episodes_without_transcript(self) -> list[PodcastEpisode]:

        items = list(
            self.container_client.query_items(
                query=f"Select * from episodes e where IS_NULL(e.transcript) OR IS_NULL(e.prediction_id)",
                enable_cross_partition_query=True,
            )
        )
        return [PodcastEpisode.model_validate(i) for i in items]

    def reset_episode_prediction_id(self, uuid: str):
        episode = self.get_episode(uuid=uuid)[0]
        episode.prediction_id = None
        self.container_client.upsert_item(episode.dict())
