# Another case of poor testing 🙁
# Oh well, at least there's something
import token

import pytest
import httpx
import tusky_users
from httpx import HTTPStatusError


BASE_URL = "http://localhost:8001"
EDITOR = BASE_URL + "/editor"


def get_user(username):
    with tusky_users.Client() as c:
        try:
            # Todo: Lol, hide test user credentials
            c.register(username=username, password="abcd1234")
        except Exception as err:
            pass
            # print("Probably duplicate users | ", err)
        bearer_token = c.login(username=username, password="abcd1234")
        access_token = bearer_token.access_token
        user_details = c.get_me(access_token)
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        return user_details, auth_headers


u1, u1_auth = get_user("u1")
u2, u2_auth = get_user("u2")


def test_quiz():

    # Assert creating a quiz
    r = httpx.post(
        "http://localhost:8001/editor/quiz",
        headers=u1_auth,
        json={"owner": u1.id, "title": "Test Quiz"},
    )
    r.raise_for_status()
    quiz_post = r.json()
    assert quiz_post["title"] == "Test Quiz"

    # Assert you can't post a quiz in someone else's name
    r = httpx.post(
        "http://localhost:8001/editor/quiz",
        headers=u2_auth,
        json={"owner": u1.id, "title": "Test Quiz"},
    )
    try:
        r.raise_for_status()
        raise ValueError(
            "Oh no! A user without proper authorization posted on someone else's account"
        )
    except HTTPStatusError:
        pass

    # Assert you need auth to post a quiz at all
    r = httpx.post(
        "http://localhost:8001/editor/quiz", json={"owner": u1.id, "title": "Test Quiz"}
    )
    try:
        r.raise_for_status()
        raise ValueError(
            "Oh no! A user without proper authorization posted on someone else's account"
        )
    except HTTPStatusError:
        pass

    # Assert getting said quiz
    r = httpx.get(
        f"http://localhost:8001/editor/quiz/",
        params={"id": quiz_post["id"]},
        headers=u1_auth,
    )
    r.raise_for_status()
    quiz_get = r.json()
    assert quiz_post == quiz_get

    # Assert modifying quiz
    patch_request = [
        # Change the quiz's title
        {"op": "replace", "path": "/title", "value": "New Title"}
    ]
    r = httpx.patch(
        f"http://localhost:8001/editor/quiz/{quiz_get['id']}",
        json=patch_request,
        headers=u1_auth,
    )
    r.raise_for_status()
    assert r.json()["title"] == "New Title"
    assert r.json()["questions"] == []

    # Assert you can't modify the snowflake
    patch_request = [
        # Change the quiz's title
        {"op": "replace", "path": "/id", "value": u2.id + 1}
    ]
    r = httpx.patch(
        f"http://localhost:8001/editor/quiz/{quiz_get['id']}",
        json=patch_request,
        headers=u1_auth,
    )
    try:
        r.raise_for_status()
        raise ValueError("Oh no! A user modified a snowflake!")
    except HTTPStatusError:
        pass
    # Assert you can't give the quiz to someone else (this will be changed later, hopefully)
    patch_request = [{"op": "replace", "path": "/owner", "value": u2.id}]
    r = httpx.patch(
        f"http://localhost:8001/editor/quiz/{quiz_get['id']}",
        json=patch_request,
        headers=u1_auth,
    )
    try:
        r.raise_for_status()
        raise ValueError("Oh no! A user gave another user a quiz without their permission!")
    except HTTPStatusError:
        pass

    # Add a question
    patch_request = [{"op": "add", "path": "/questions/1", "value": {"query": "How much wood could a woodchuck chuck if a woodchuck could chuck wood?"}}]
    r = httpx.patch(
        f"http://localhost:8001/editor/quiz/{quiz_get['id']}",
        json=patch_request,
        headers=u1_auth,
    )
    print(r.content)
    r.raise_for_status()
    print(r.json())




if __name__ == "__main__":
    test_quiz()
