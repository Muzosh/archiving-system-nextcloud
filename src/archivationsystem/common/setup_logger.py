import logging

from python_logging_rabbitmq import RabbitMQHandlerOneWay


def setup_logger(config: dict):
    logger = logging.getLogger("archiving_system_logging")
    logger.addHandler(
        RabbitMQHandlerOneWay(
            host=config.get("host"),
            port=config.get("port"),
            username=config.get("username"),
            password=config.get("password"),
            connection_params={
                "virtual_host": "archivingsystem",
            },
        )
    )
    logger.setLevel(config.get("logging_level"))
