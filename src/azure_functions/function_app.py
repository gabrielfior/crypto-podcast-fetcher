import azure.functions as func
import datetime
import json
import logging

# from src.crypto_podcasts.config import TaddyApiKey, DBConfig
# from src.crypto_podcasts.data_fetching.constants import PODCAST_UUIDS
# from src.crypto_podcasts.data_fetching.cosmos_handler import CosmosClient
# from src.crypto_podcasts.data_fetching.podcast_fetcher import PodcastFetcher

app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 */1 * * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def timer_trigger(myTimer: func.TimerRequest) -> None:

    if myTimer.past_due:
        logging.info("The timer is past due!")

    logging.info(
        f"Python timer trigger function started. Time {datetime.datetime.utcnow()}"
    )

    run()

    logging.info(
        f"Python timer trigger function finished. Time {datetime.datetime.utcnow()}"
    )


def run() -> None:
    pass
    # # Fetch all episodes from last week from the given list.
    # # Store transcript on Cosmos.
    # pf = PodcastFetcher(api_key=TaddyApiKey())
    # cosmos_client = CosmosClient(db_config=DBConfig())
    # for uuid in PODCAST_UUIDS:
    #     episodes = pf.fetch_podcast_episodes_from_last_week(podcast_uuid=uuid)
    #     # Store transcript
    #     for episode in episodes:
    #         logging.info(f"Storing episode {episode}")
    #         cosmos_client.store_episode_if_not_exists(episode)


if __name__ == "__main__":
    run()
