"""
Sprint B03-S006 — Application Lifecycle
"""

from builder.shared.config import ApplicationSettings
from builder.shared.logger import Logger


class Application:
    def __init__(self):
        self.settings = ApplicationSettings()
        self.logger = Logger()

    def launch(self) -> None:
        self.logger.info("Launching application")

    def initialise(self) -> None:
        self.logger.info("Initialising application")

    def shutdown(self) -> None:
        self.logger.info("Shutting down application")

    def run(self) -> None:
        self.launch()
        self.initialise()
        self.logger.info(
            f"{self.settings.application_name} v{self.settings.version}"
        )
        self.shutdown()
