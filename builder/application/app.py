from builder.shared.config import ApplicationSettings
from builder.shared.logger import Logger

class Application:
    def __init__(self):
        self.settings=ApplicationSettings()
        self.logger=Logger()

    def run(self):
        self.logger.info(f"{self.settings.application_name} v{self.settings.version}")
