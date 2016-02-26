"""
Python misses an easy way to implement a singleton.
"""


class SingletonMeta(type):
    """
    Make a class a singleton.
    Add ``metaclass=SingletonMeta`` to the class' options to make it a singleton.
    """
    __instances = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]

    @classmethod
    def delete(mcs, instance_type: type) -> None:
        """
        Delete a singleton instance

        :param type instance_type: The type to clear an instance of
        """
        if instance_type in mcs.__instances:
            del mcs.__instances[instance_type]
