def add_env_suffix(func):
    def wrapper(self, table_name: str, *args, **kwargs):
        if "env" in kwargs and kwargs["env"]:
            table_name += "-prod"
        else:
            table_name += "-dev"

        return func(self, table_name, *args, **kwargs)

    return wrapper