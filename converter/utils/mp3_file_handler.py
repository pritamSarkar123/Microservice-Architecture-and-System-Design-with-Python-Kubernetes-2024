import time

from config.config import Settings
from pymongo import MongoClient
from datetime import datetime, timedelta

def check_and_remove_old_mp3s(settings):
    mongo_client = None

    while True:
        time.sleep(10)
        try:
            mongo_client = MongoClient(
                f"mongodb://{settings.mongo_username}:{ settings.mongo_password}@{settings.mongo_host}:{settings.mongo_port}"
            )
            db_mp3_id_maps = mongo_client.mp3_id_maps
            # one_hour_ago_str = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            one_hour_ago_str = datetime.now() - timedelta(hours=1)
            db_mp3_id_maps["mp3_id_maps"].delete_many({"created_at": {"$lt": one_hour_ago_str}})
            
        except Exception as e:
            print(
                f"Failed to create connection with mongodb. Error: {str(e)}"
            )
            time.sleep(2)
        finally:
            try:
                if mongo_client is not None:
                    mongo_client.close()
            except:
                pass
        
def handle_old_mp3_files(settings):
    check_and_remove_old_mp3s(settings)


