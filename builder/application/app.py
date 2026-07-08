"""
Application skeleton.

Sprint: B03-S004 — Logging Framework
"""
from builder.shared.config import ApplicationSettings
from builder.shared.logger import Logger

class Application:
    def __init__(self)->None:
        self.settings=ApplicationSettings()
        self.logger=Logger()

    def run(self)->None:
        self.logger.info(f"{self.settings.application_name} v{self.settings.version}")
