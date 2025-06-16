from pathlib import Path
import json


class User:
    def __init__(self, username=Path.home().name, phone='', pointer_user=Path.home().name, pointer=True, late_rides=True, batteries=True, long_rides=True):
        self.username = username
        self.phone = phone
        self.pointer_user = pointer_user or username
        self.pointer = pointer
        self.late_rides = late_rides
        self.batteries = batteries
        self.long_rides = long_rides
        self.code = None
        
    def __repr__(self):
        return f"User(username={self.username}, phone={self.phone}, pointer_username={self.pointer_user}, pointer={self.pointer}, late_rides={self.late_rides}, batteries={self.batteries}, long_rides={self.long_rides})"
    
    def to_dict(self):
        return {
            'username': self.username,
            'phone': self.phone,
            'pointer_user': self.pointer_user,
            'pointer': self.pointer,
            'late_rides': self.late_rides,
            'batteries': self.batteries,
            'long_rides': self.long_rides
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            username=data.get('username', Path.home().name),
            phone=data.get('phone', ''),
            pointer_user=data.get('pointer_user', data.get('username', Path.home().name)),
            pointer=data.get('pointer', True),
            late_rides=data.get('late_rides', True),
            batteries=data.get('batteries', True),
            long_rides=data.get('long_rides', True)
        )
    
    @classmethod
    def from_json(cls, json_path: str | Path):
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
        