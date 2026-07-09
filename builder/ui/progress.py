"""
Sprint B03-S009 — Progress Framework
"""

class ProgressPanel:
    def __init__(self):
        self.current = 0
        self.total = 100

    def update(self, current:int, total:int=100)->None:
        self.current=current
        self.total=total

    def render(self)->None:
        percent=(self.current/self.total)*100 if self.total else 0
        print(f"Progress: {percent:.0f}%")
