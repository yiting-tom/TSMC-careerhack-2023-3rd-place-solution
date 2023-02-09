from dataclasses import dataclass
from models.share import Share

def dict_to_objects(cls: dataclass):
    def decorator(func: callable):
        def batch_dict_to_objects(dicts):
            if isinstance(dicts, dict):
                return cls.from_dict(dicts)
            if cls == Share:
                print('\n'*3, dicts)

            return [
                cls.from_dict(dic)
                for dic in dicts
            ]

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return batch_dict_to_objects(result)

        return wrapper
    return decorator