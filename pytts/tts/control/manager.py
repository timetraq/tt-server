"""
This holds stuff to manage our server instance
"""

from ..util.singleton import SingletonMeta


class ControlManager(object, metaclass=SingletonMeta):
    """
    The Control Manager manages the server instance, like startup and shutdown
    """

    __initialized = False

    def __init__(self, no_init: bool=False) -> None:
        """
        Initialize with default settings
        :param bool no_init: Do not perform an initialization, because configuration is already on the way
        """
        if no_init:
            return
        self.__initialized = True

    def configure(self, argv: list=None) -> None:
        """
        Configure with command line arguments
        :param list[str] argv: Command line arguments
        :raises RuntimeError: when already initialized
        """
        if self.initialized:
            raise RuntimeError('ControlManager already initialized')
        self.__initialized = True
        if argv is None:
            return

    @property
    def initialized(self) -> bool:
        """
        Is the class already initialized?
        :return: true, when the class is already initialized
        :rtype: bool
        """
        return self.__initialized

    @staticmethod
    def factory(argv: list=None) -> 'ControlManager':
        """
        Create a new Control Manager with command line arguments (optional)

        :param list[str] argv: optional command line arguments
        :rtype: ControlManager
        :return: newly created and configured instance
        :raises RuntimeError: when factory was already run
        """
        control_manager = ControlManager(no_init=True)
        if control_manager.initialized:
            raise RuntimeError('ControlManager already initialized')
        control_manager.configure(argv)
        return control_manager
