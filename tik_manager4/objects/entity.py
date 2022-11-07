import uuid
import os
from tik_manager4.objects.guard import Guard
from tik_manager4.core import filelog

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

class Entity(object):
    # _user = User()
    guard = Guard()

    def __init__(self, name="", uid=None):
        self._id = uid
        self._relative_path = ""
        self._name = name
        self.__mode = "entity"
        # self._user = User()

    @property
    def id(self):
        if not self._id:
            self._id = uuid.uuid1().time_low
        return self._id

    @id.setter
    def id(self, val):
        self._id = val

    @property
    def path(self):
        return self._relative_path.replace("\\", "/")

    @path.setter
    def path(self, val):
        self._relative_path = val

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def permission_level(self):
        return self.guard.permission_level

    @property
    def is_authenticated(self):
        return self.guard.is_authenticated

    def _check_permissions(self, level):
        """Checks the user permissions for project actions."""
        if self.permission_level < level:
            log.warning("This user does not have permissions for this action")
            return -1

        if not self.is_authenticated:
            log.warning("User is not authenticated")
            return -1
        return 1

    def get_abs_database_path(self, *args):
        return os.path.normpath(os.path.join(self.guard.database_root, self.path, *args))
    def get_abs_project_path(self, *args):
        return os.path.normpath(os.path.join(self.guard.project_root, self.path, *args))
    def get_purgatory_project_path(self, *args):
        return os.path.normpath(os.path.join(self.guard.project_root, "__purgatory", self.path, *args))
    def get_purgatory_database_path(self, *args):
        return os.path.normpath(os.path.join(self.guard.project_root, "__purgatory", "tikDatabase", self.path, *args))