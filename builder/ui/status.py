"""
Sprint B03-S008 — Status System
"""

class StatusPanel:
    def __init__(self):
        self.status="Idle"

    def set_status(self,status:str)->None:
        self.status=status

    def render(self)->None:
        print(f"Status: {self.status}")
