# MODIFIED FROM IGIBSON REPO

import os
from abc import abstractmethod
from mini_behavior.rendering import *

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

    def __init__(self, obj, key): # env
        super(BaseObjectState, self).__init__()
        self.obj = obj
        self.name = key

    # def update(self, *args, **kwargs):
    #     # assert self._initialized, "Cannot update uninitalized state."
    #     self._update(*args, **kwargs)

    def get_value(self, *args, **kwargs):
        # assert self._initialized
        self._update(*args, **kwargs)
        return self._get_value(*args, **kwargs)

    def set_value(self, *args, **kwargs):
        # assert self._initialized
        return self._set_value(*args, **kwargs)

    def check_dependencies(self, env):
        pass


class AbsoluteObjectState(BaseObjectState):
    """
    track object states that are absolute (require seed 0_2 object)
    """
    def __init__(self, obj, key): # env
        super(AbsoluteObjectState, self).__init__(obj, key)
        self.type = 'absolute'
        self.value = False

    def _update(self, env=None):
        pass

    def _get_value(self, env=None):
        return self.value

    def _set_value(self, new_value):
        self.value = new_value


class RelativeObjectState(BaseObjectState):
    """
    This class is used to track object states that are relative, e.g. require two objects to compute a value.
    Note that subclasses will typically compute values on-the-fly.
    """
    def __init__(self, obj, key): # env
        super(RelativeObjectState, self).__init__(obj, key)
        self.type = 'relative'

    def _update(self, other, env=None):
        pass

    def _get_value(self, other, env=None):
        raise NotImplementedError

    def _set_value(self, other, new_value):
        pass


class ObjectProperty(BaseObjectState):
    """
    track object states that are absolute (require seed 0_2 object)
    """
    def __init__(self, obj, key): # env
        super(ObjectProperty, self).__init__(obj, key)
        self.type = 'absolute'

    @staticmethod
    def _update(self):
        pass

    @staticmethod
    def _get_value(self, env=None):
        return True

    def _set_value(self, new_value):
        pass


class AbilityState(AbsoluteObjectState):
    def __init__(self, obj, key):
        super().__init__(obj, key)
        icon_path = os.path.join(os.path.dirname(__file__), f'../utils/state_icons/{key}.jpg')
        self.icon = img_to_array(icon_path)

    def render(self, img, value=False):
        color = [0, 255, 0] if value else [255, 255, 255]
        fill_coords(img, point_in_icon(img, self.icon), color)
