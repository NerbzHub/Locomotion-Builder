from dataclasses import dataclass

@dataclass(frozen=True)
class ApplicationSettings:
    application_name:str="Locomotion Builder"
    version:str="0.7.0"
