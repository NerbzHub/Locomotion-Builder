from builder.shared.config import ApplicationSettings
from builder.shared.logger import Logger
from builder.ui.console import ConsoleUI
from builder.ui.status import StatusPanel

class Application:
    def __init__(self):
        self.settings=ApplicationSettings()
        self.logger=Logger()
        self.ui=ConsoleUI()
        self.status=StatusPanel()

    def launch(self):
        self.status.set_status("Launching")
        self.logger.info("Launching application")

    def initialise(self):
        self.status.set_status("Initialising")
        self.logger.info("Initialising application")
        self.ui.render()
        self.status.render()

    def shutdown(self):
        self.status.set_status("Shutdown")
        self.logger.info("Shutting down application")

    def run(self):
        self.launch()
        self.initialise()
        self.logger.info(f"{self.settings.application_name} v{self.settings.version}")
        self.shutdown()
