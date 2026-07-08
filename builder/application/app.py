from builder.shared.config import ApplicationSettings

class Application:
    def __init__(self):
        self.settings=ApplicationSettings()
    def run(self):
        print(self.settings.application_name)
        print(f"Version {self.settings.version}")
