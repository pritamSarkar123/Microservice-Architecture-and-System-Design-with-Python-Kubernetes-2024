import json
import os
import tempfile

import moviepy.editor
import pika
from datetime import datetime
from bson.objectid import ObjectId


def start(message, fs_videos, fs_mp3s, channel, db_mp3_id_maps):
    message = json.loads(message)

    # create empty temp file
    tf = tempfile.NamedTemporaryFile(delete=True)

    # get video contents
    out = fs_videos.get(ObjectId(message["video_fid"]))

    # add video contents to empty file
    tf.write(out.read())

    # convert to mp3
    audio = moviepy.editor.VideoFileClip(tf.name).audio

    tf.close()

    fs_videos.delete(ObjectId(message["video_fid"]))

    # write audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # save file to mongo
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()

    os.remove(tf_path)
    message["mp3_fid"] = str(fid)
    message["created_at"] = current_date_time =datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    db_mp3_id_maps["mp3_id_maps"].insert_one({"mp3_id": str(fid), "created_at": current_date_time})

    try:
        channel.basic_publish(
            exchange="",
            routing_key="mp3",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        fs_mp3s.delete(fid)
        return "failed to publish message"
