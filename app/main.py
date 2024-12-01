from settings import settings
from ampq import Session
from pipeline import Pipeline
import json
import pika
import time
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
import logging
from vectorstore import StorageBM

session = Session()
pipeline = Pipeline()

session.set_connection_params(
    host=str(settings.ampq_host),
    port=settings.ampq_port,
    virtual_host=settings.ampq_vir_host,
    username=settings.ampq_user,
    password=settings.ampq_password,
)


@session.on_message
def on_message(channel: BlockingChannel, method: Basic.Deliver,
               properties: pika.BasicProperties, body: bytes):

    start = time.time()
    value = json.loads(body.decode().replace("'", '"'))

    id = value['request_id']
    logging.info(f"Going to process {id}")
    target_file = value["target_file_url"]
    instructions = value["instructions_file_url"]
    last_date = value["last_modified_dttm"]



    # store = StorageBM()
    # store.add(docs) # pass text of instruction

    # res = pipeline(code, store)


    send = {
        "request_id": id,
        "report_content": "test",
        "status": "success"
    }
    session.publish(
        exchange="",
        routing_key=settings.queue_back,
        body=json.dumps(send),
        properties=pika.BasicProperties(
            content_type='application/json'
        )
    )

    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    session.start_consuming(
        settings.queue_in,
        prefetch_count=settings.prefetch_count
    )
