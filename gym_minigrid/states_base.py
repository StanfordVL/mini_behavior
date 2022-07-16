# MODIFIED FROM IGIBSON REPO

from abc import abstractmethod

class BaseObjectState:
    """
    Base ObjectState class. Do NOT inherit from this class directly - use either AbsoluteObjectState or
    RelativeObjectState.
    """

    @staticmethod
    def get_dependencies():
        """
        Get the dependency states for this state, e.g. states that need to be explicitly enabled on the current object
        before the current state is usable. States listed here will be enabled for all objects that have this current
        state, and all dependency states will be processed on *all* objects prior to this state being processed on
        *any* object.
        :return: List of strings corresponding to state keys.
        """
        return []

    @staticmethod
    def get_optional_dependencies():
        """
        Get states that should be processed prior to this state if they are already enabled. These states will not be
        enabled because of this state's dependency on them, but if they are already enabled for another reason (e.g.
        because of an ability or another state's dependency etc.), they will be processed on *all* objects prior to this
        state being processed on *any* object.
        :return: List of strings corresponding to state keys.
        """
        return []

    def __init__(self, obj): # env
        super(BaseObjectState, self).__init__()
        self.obj = obj
        # self._initialized = False
        # self.env = env

    def _update(self):
        """This function will be called once for every simulator step."""
        pass

    # def _initialize(self):
    #     """This function will be called once, after the object has been loaded."""
    #     pass
    #
    # def initialize(self, simulator):
    #     assert not self._initialized, "State is already initialized."
    #
    #     self.simulator = simulator
    #     self._initialize()
    #     self._initialized = True

    def update(self):
        # assert self._initialized, "Cannot update uninitalized state."
        return self._update()

    def get_value(self, *args, **kwargs):
        # assert self._initialized
        return self._get_value(*args, **kwargs)

    def set_value(self, *args, **kwargs):
        # assert self._initialized
        return self._set_value(*args, **kwargs)


class AbsoluteObjectState(BaseObjectState):
    """
    track object states that are absolute (require 1 object)
    """
    def __init__(self, obj): # env
        super(BaseObjectState, self).__init__()
        self.obj = obj
        self.type = 'absolute'

    @abstractmethod
    def _get_value(self, env):
        raise NotImplementedError()

    # @abstractmethod
    def _set_value(self, new_value):
        # raise NotImplementedError()
        pass

    # NOTE: DUMP / LOAD ARE RELATED TO THE SIMULATOR. UNSURE IF NEED THIS
    # @abstractmethod
    # def _dump(self):
    #     raise NotImplementedError()
    #
    # def dump(self):
    #     assert self._initialized
    #     return self._dump()
    #
    # @abstractmethod
    # def load(self, data):
    #     raise NotImplementedError()


class RelativeObjectState(BaseObjectState):
    """
    This class is used to track object states that are relative, e.g. require two objects to compute a value.
    Note that subclasses will typically compute values on-the-fly.
    """
    def __init__(self, obj): # env
        super(BaseObjectState, self).__init__()
        self.obj = obj
        self.type = 'relative'

    @abstractmethod
    def _get_value(self, other, env):
        raise NotImplementedError()

    # @abstractmethod
    def _set_value(self, other, new_value):
        pass


class StaticObjectState(BaseObjectState):
    """
    This class is used to track object states that cannot change
    """
    def __init__(self, obj): #, env):
        super(StaticObjectState, self).__init__(obj) #, env)
        self.value = True
        self.type = 'static'

    def _get_value(self):
        return self.value

    def _set_value(self, new_value):
        self.value = new_value
