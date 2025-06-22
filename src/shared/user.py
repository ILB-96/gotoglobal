from pathlib import Path
import json
from services.fluent.qfluentwidgets import ConfigItem, BoolValidator, ConfigValidator


class User:
    def __init__(
        self,
        username=None,
        phone='',
        pointer_user=None,
        pointer=True,
        late_rides=True,
        batteries=True,
        long_rides=True
    ):
        self.username = username or Path.home().name
        self.late_rides = ConfigItem('gotoGroup', "lateRides", late_rides,  BoolValidator())
        self.long_rides = ConfigItem('autotelGroup',"longRides", long_rides,  BoolValidator())
        self.batteries = ConfigItem('autotelGroup', "batteries", batteries,  BoolValidator())
        self.pointer = ConfigItem('othersGroup',"pointer", pointer,  BoolValidator())
        self.phone = ConfigItem('othersGroup',"phone", "" if phone is None else phone, ConfigValidator())
        self.pointer_user = ConfigItem('othersGroup', "pointerUser", pointer_user or self.username, ConfigValidator())
        self.code = None  # Internal use (optional)

    def __repr__(self):
        return (
            f"User(username={self.username}, phone={self.phone}, "
            f"pointer_username={self.pointer_user}, pointer={self.pointer}, "
            f"late_rides={self.late_rides}, batteries={self.batteries}, long_rides={self.long_rides})"
        )
    def _val(self, x):
        return x.value if isinstance(x, ConfigItem) else x

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "phone": self._val(self.phone),
            "pointer_user": self._val(self.pointer_user),
            "pointer": self._val(self.pointer),
            "late_rides": self._val(self.late_rides),
            "batteries": self._val(self.batteries),
            "long_rides": self._val(self.long_rides)
        }


    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            username=data.get("username", Path.home().name),
            phone=data.get("phone", ""),
            pointer_user=data.get("pointer_user", data.get("username", Path.home().name)),
            pointer=data.get("pointer", True),
            late_rides=data.get("late_rides", True),
            batteries=data.get("batteries", True),
            long_rides=data.get("long_rides", True)
        )

    @classmethod
    def from_json(cls, json_path: str | Path) -> "User":
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_json(self, json_path: str | Path):
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
