import os

import dotenv
from flask import Flask


BYPASS_SAFETY_CHECKPOINTS = False


def load_config(app: Flask):
    global BYPASS_SAFETY_CHECKPOINTS

    dotenv.load_dotenv(verbose=True)
    print(dotenv.find_dotenv())

    if os.getenv("BYPASS_CHECKPOINT_SAFETY_NETS", 0) == str(1):
        app.logger.error("WARNING: safety nets disabled, players can cheat")
        BYPASS_SAFETY_CHECKPOINTS = True
