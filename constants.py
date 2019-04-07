import ConfigParser


config_path = 'config.ini'
config = ConfigParser.ConfigParser()
config.read(config_path)
SKIPLAGGED_HOST = config.get("SKIPLAGGED", "HOST")
SKIPLAGGED_URL = config.get("SKIPLAGGED", "URL")
SKIPTRIP_HOST = config.get("SKIPTRIP", "HOST")
SKIPTRIP_URL = config.get("SKIPTRIP", "URL")