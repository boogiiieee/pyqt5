from environs import Env

env = Env()
env.read_env(".env")

WINDOW_TITLE = env.str("WINDOW_TITLE")
WINDOW_LEFT = env.int("WINDOW_LEFT")
WINDOW_TOP = env.int("WINDOW_TOP")
WINDOW_WIDTH = env.int("WINDOW_WIDTH")
WINDOW_HEIGHT = env.int("WINDOW_HEIGHT")
TIMER_INTERVAL = env.int("TIMER_INTERVAL")
