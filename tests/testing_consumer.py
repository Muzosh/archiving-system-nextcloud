import logging
import sys
from pathlib import Path, PurePath

from common.setup_logger import setup_logger
from common.yaml_parser import parse_yaml_config
from rabbitmq_connection.task_consumer import ConnectionMaker, TaskConsumer

logger = logging.getLogger("Archivation System")


def run(config):
    connection = ConnectionMaker(config.get("rabbitmq_connection"))
    task_consumer = TaskConsumer(connection, config.get("rabbitmq_info"))
    task_consumer.set_callback(job)
    task_consumer.start()


def job(body):

    print(body)
    return


def main():
    """
    takes 2 system arguments:
        -c | --config   => configuration file for consumer
    """
    args = sys.argv[1:]
    if not (len(args) == 2):
        raise SystemExit(
            f"Usage: {sys.argv[0]} (-c | --config) <path to yaml config>"
        )
    config_path = None
    if args[0] == "-c" or args[0] == "--config":
        config_path = Path(args[1])
    if not isinstance(config_path, PurePath):
        raise SystemExit(
            f"Usage: {sys.argv[0]} (-c | --config) <path to yaml config>"
        )
    parsed_config = parse_yaml_config(config_path)
    setup_logger(parsed_config.get("rabbitmq_logging"))
    run(parsed_config)


if __name__ == "__main__":
    main()