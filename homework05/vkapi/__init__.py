from vkapi import config  # type: ignore
from vkapi.session import Session  # type: ignore

session = Session(config.VK_CONFIG["domain"])
