from typing import Dict, List, Iterator
from copy import copy


class BadManifestFile(BaseException):
    """
    Thrown when the server fails to parse a manifest file.
    """
    def __init__(self, reason: str) -> None:
        msg = "bad manifest file: {}".format(reason)
        super().__init__(msg)


class UnexpectedStatusCode(BaseException):
    """
    Indicates that the API request produced an unexpected status code.
    """
    def __init__(self, code: int) -> None:
        self.__code = code
        super().__init__("API request produced unexpected status code: {}".format(code))

    @property
    def code(self) -> int:
        """
        The unexpected status code that was produced by the API request.
        """
        return self.__code


class BugAlreadyBuilt(BaseException):
    """
    Indicates that the given bug has already been installed on the server.
    """
    def __init__(self, name: str) -> None:
        self.__name = name
        super().__init__("bug already built: {}".format(name))

    @property
    def name(self) -> str:
        """
        The name of the bug.
        """
        return self.__name


class BugNotFound(BaseException):
    """
    Indicates that no bug was found that matches the provided identifier.
    """
    def __init__(self, name: str) -> None:
        self.__name = name
        super().__init__("no bug found with name: {}".format(name))

    @property
    def name(self) -> str:
        """
        The name of the requested bug.
        """
        return self.__name


class SourceNotFoundWithURL(BaseException):
    """
    Indicates that no source has been found that matches a provided URL.
    """
    def __init__(self, url: str) -> None:
        self.__url = url
        super().__init__("no source registered with URL: {}".format(url))

    @property
    def url(self) -> str:
        return self.__url


class SourceNotFoundWithName(BaseException):
    """
    Indicates that there exists no source registered with a given name.
    """
    def __init__(self, name: str) -> None:
        self.__name = name
        super().__init__("no source registered with name: {}".format(name))

    @property
    def name(self) -> str:
        return self.__name


class SourceAlreadyRegisteredWithURL(BaseException):
    """
    Indicates that there exists a source that is already registered with a
    given URL.
    """
    def __init__(self, url: str) -> None:
        self.__url = url
        super().__init__("source already registered with URL: {}".format(url))

    @property
    def url(self) -> str:
        return self.__url


class NameInUseError(BaseException):
    """
    Indicates that a given name is already in use by another resource.
    """
    def __init__(self, name: str) -> None:
        self.__name = name
        super().__init__("name already in use: {}".format(name))

    @property
    def name(self) -> str:
        return self.__name


class BugNotInstalledError(BaseException):
    """
    Indicates that a given bug hasn't been installed.
    """
    def __init__(self, name: str) -> None:
        self.__name = name
        super().__init__("bug not installed: {}".format(name))

    @property
    def name(self) -> str:
        """
        The name of the bug that is not installed.
        """
        return self.__name


class ImageBuildFailed(BaseException):
    """
    Indicates that an attempt to build a given Docker image has failed.
    """
    def __init__(self,
                 image_name: str,
                 log: List[Dict[str, str]]
                 ) -> None:
        self.__image_name = image_name
        self.__log = copy(log)
        msg = "failed to build image: {}".format(image_name)
        super().__init__(image_name)

    @property
    def image_name(self) -> str:
        """
        The name of the image that failed to build.
        """
        return self.__image_name

    @property
    def log(self) -> Iterator[Dict[str, str]]:
        """
        A log of the failed build attempt.
        """
        for entry in self.__log:
            yield entry
