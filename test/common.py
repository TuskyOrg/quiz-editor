__all__ = ["u1", "u1_auth", "u2", "u2_auth", "ImmutableDict"]
import tusky_users


def get_user(username):
    with tusky_users.Client() as c:
        try:
            # Todo: Lol, hide test user credentials
            c.register(username=username, password="abcd1234")
        except Exception as err:
            pass
        bearer_token = c.login(username=username, password="abcd1234")
        access_token = bearer_token.access_token
        user_details = c.get_me(access_token)
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        return user_details, auth_headers


u1, u1_auth = get_user("u1")
u2, u2_auth = get_user("u2")


class ImmutableDict(dict):
    # Reference: https://www.python.org/dev/peps/pep-0351/#id11
    def __hash__(self):
        return id(self)

    def _immutable(self, *args, **kws):
        raise TypeError('object is immutable')

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear       = _immutable
    update      = _immutable
    setdefault  = _immutable
    pop         = _immutable
    popitem     = _immutable
