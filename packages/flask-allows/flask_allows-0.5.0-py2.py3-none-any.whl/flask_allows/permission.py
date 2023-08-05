import warnings
from .allows import allows, _make_callable


class Permission(object):
    """
    Used to check requirements as a boolean or context manager. When used as a
    boolean, it only runs the requirements and returns the raw boolean result::

        p = Permission(is_admin)

        if p:
            print("Welcome to the club!")


    When used as a context manager, it runs both the check and the failure
    handlers if the requirements are not met::

        p = Permission(is_admin)

        with p:
            # will run on_fail and throw before reaching if the
            # requirements on p return False
            print("Welcome to the club!")


    :param requirements: The requirements to check against
    :param throws: Optional, keyword only. Exception to throw when used as a context manager,
        if provided it takes precedence over the exception stored on the current
        application's registered :class:`~flask_allows.allows.Allows` instance
    :param on_fail: Optional, keyword only. Value or function to use as the on_fail when used
        as a context manager, if provided takes precedence over the on_fail
        configured on current application's registered
        :class:`~flask_allows.allows.Allows` instance
    :param identity: Optional, keyword only. An identity to verify against
        instead of the using the loader configured on the current application's
        registered :class:`~flask_allows.allows.Allows` instance

    """

    def __init__(self, *requirements, **opts):
        self.ext = allows._get_current_object()
        self.requirements = requirements
        self.throws = opts.get('throws', self.ext.throws)
        self.identity = opts.get('identity')
        self.on_fail = _make_callable(opts.get('on_fail', self.ext.on_fail))

    @property
    def throw_type(self):
        warnings.warn(
            "Permission.throw_type is deprecated and will be removed in 0.6",
            DeprecationWarning,
            stacklevel=2
        )
        if isinstance(self.throws, type):
            return self.throws
        else:
            return type(self.throws)

    def __bool__(self):
        return self.ext.fulfill(self.requirements, identity=self.identity)

    __nonzero__ = __bool__

    def __enter__(self):
        if not self:
            self.on_fail()
            raise self.throws

    def __exit__(self, exctype, value, tb):
        pass
