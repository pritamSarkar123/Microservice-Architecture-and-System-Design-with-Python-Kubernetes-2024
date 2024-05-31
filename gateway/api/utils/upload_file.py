import json

import pika
from ..queue import get_connections

# upload(content, fs, channel, metadata=token_validation_dict)


async def upload(file_content, fs, metadata):
    try:
        fid = fs.put(file_content)
    except Exception as e:
        return f"Internal server error due to : {str(e)}"

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": metadata["email"],
    }

    try:
        channel, connection = get_connections()
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as e:
        fs.delete(fid)
        return f"Internal server error due to : {str(e)}"
    finally: 
        if channel is not None:
            channel.close()
        if connection is not None:
            connection.close()
