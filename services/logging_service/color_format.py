from colorlog import ColoredFormatter

color_formatter = ColoredFormatter(
    (
        "%(log_color)s%(levelname)-5s%(reset)s "
        "%(yellow)s[%(asctime)s]%(reset)s"
        "%(white)s (%(filename)s:%(lineno)d %(bold_purple)s in %(white)s %(funcName)s()) %(bold_purple)s--%(reset)s "
        "%(log_color)s%(message)s%(reset)s"
    ),
    datefmt="%d-%m-%Y %H:%M:%S",
    log_colors={
        "DEBUG": "blue",
        "INFO": "green",
        "WARNING": "red",
        "ERROR": "bg_bold_red",
        "CRITICAL": "red,bg_white",
    },
)
