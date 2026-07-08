"""
Sprint B03-S007 — Application Lifecycle + UI Shell
"""
from builder.shared.config import ApplicationSettings
from builder.shared.logger import Logger
from builder.ui.console import ConsoleUI

class Application:
    def __init__(self):
        self.settings=ApplicationSettings()
        self.logger=Logger()
        self.ui=ConsoleUI()

    def launch(self):
        self.logger.info("Launching application")

    def initialise(self):
        self.logger.info("Initialising application")
        self.ui.render()

    def shutdown(self):
        self.logger.info("Shutting down application")

    def run(self):
        self.launch()
        self.initialise()
        self.logger.info(f"{self.settings.application_name} v{self.settings.version}")
        self.shutdown()
