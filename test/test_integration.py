# Another case of poor testing 🙁
# Oh well, at least there's something
# fmt: off
import json

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
    ####################################################################################
    # Assert creating a quiz
    r = httpx.post(
        "http://localhost:8001/editor/quiz",
        headers=u1_auth,
        json={"owner": u1.id, "title": "Test Quiz"},
    )
    r.raise_for_status()
    quiz_post = r.json()
    assert quiz_post["title"] == "Test Quiz"
    print(f"posted quiz:\t{r.json()}")

    ####################################################################################
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

    ####################################################################################
    # Assert getting said quiz
    r = httpx.get(
        f"http://localhost:8001/editor/quiz/",
        params={"id": quiz_post["_id"]},
        headers=u1_auth,
    )
    r.raise_for_status()
    quiz_get = r.json()
    assert quiz_post == quiz_get

    ####################################################################################
    # Assert modifying quiz
    patch_request = [
        # Change the quiz's title
        {"op": "replace", "path": "/title", "value": "New Title"}
    ]
    r_patch = httpx.patch(
        f"http://localhost:8001/editor/quiz/{quiz_get['_id']}",
        content=json.dumps(patch_request),
        headers=u1_auth,
    )
    print("Request content:\t", r_patch.request.content)
    r_patch.raise_for_status()
    assert r_patch.json()["title"] == "New Title"
    assert r_patch.json()["questions"] == []

    ####################################################################################
    # Assert the quiz was ACTUALLY modified
    r_get = httpx.get(
        f"http://localhost:8001/editor/quiz/",
        params={"id": quiz_post["_id"]},
        headers=u1_auth,
    )
    r_get.raise_for_status()
    assert (
        r_patch.json() == r_get.json()
    ), f"\nORIGINAL _ID:\t{quiz_get['_id']}\nPATCHED JSON:\t{r_patch.json()}\nGOTTEN JSON:\t{r_get.json()}"

    ####################################################################################
    # Assert you can't modify the snowflake
    patch_request = [
        # Change the quiz's title
        {"op": "replace", "path": "/id", "value": u2.id + 1}
    ]
    r = httpx.patch(
        f"http://localhost:8001/editor/quiz/{quiz_get['_id']}",
        json=patch_request,
        headers=u1_auth,
    )
    try:
        r.raise_for_status()
        raise ValueError("Oh no! A user modified a snowflake!")
    except HTTPStatusError:
        pass

    ####################################################################################
    # Assert you can't give the quiz to someone else (this will be changed later, hopefully)
    patch_change_owner = [{"op": "replace", "path": "/owner", "value": u2.id}]
    r = httpx.patch(
        f"http://localhost:8001/editor/quiz/{quiz_get['_id']}",
        json=patch_change_owner,
        headers=u1_auth,
    )
    try:
        r.raise_for_status()
        raise ValueError(
            "Oh no! A user gave another user a quiz without their permission!"
        )
    except HTTPStatusError:
        pass

    ####################################################################################
    # ASSERT PATCH MUST BE LIST
    question = {"query": "q1", "answers": [{"text": "q1a1"}, {"text": "q1a2", "points": 1}]}


    patch_request = {
        "op": "add",
        "path": "/questions/0",
        "value": question,
    }

    r = httpx.patch(
        f"http://localhost:8001/editor/quiz/{quiz_get['_id']}",
        content=json.dumps(patch_request),
        headers=u1_auth,
    )
    try:
        r.raise_for_status()
        raise ValueError("The server let a bad request through")
    except HTTPStatusError:
        pass

    ####################################################################################
    # Add a question
    patch_request = [{
        "op": "add",
        "path": "/questions/0",
        "value": question,
    }]
    r = httpx.patch(
        f"http://localhost:8001/editor/quiz/{quiz_get['_id']}",
        content=json.dumps(patch_request),
        headers=u1_auth,
    )
    r.raise_for_status()

    q = r.json()["questions"][0]
    print(r.json())
    assert q["query"] == "q1", f"Adding a question did not work properly\n{q}"
    if "id" in q:
        raise ValueError("The question id was not reset")
    if "id" in q["answers"][0]:
        raise ValueError("The answer's id was reset")
    if len({q["_id"], q["answers"][0]["_id"], q["answers"][1]["_id"]}) != 3:
        raise ValueError(
            "The answer's snowflake was mistakenly set equal to the question's snowflake"
        )
    assert r.json()["title"] == "New Title"
    assert r.json()["questions"][0]["answers"][0]["points"] == 0
    assert r.json()["questions"][0]["answers"][1]["text"] == "q1a2"
    assert r.json()["questions"][0]["answers"][1]["points"] == 1

    ####################################################################################
    # Add more questions
    q2 = {"query": "q2", "answers": [{"text": "q2a1"}, {"text": "q2a2", "points": 1}]}
    q3 = {"query": "q3", "answers": [{"text": "q3a1"}, {"text": "q3a2", "points": 1}]}
    q4 = {"query": "q4", "answers": [{"text": "q4a1"}, {"text": "q4a2", "points": 1}]}

    patch_request = [
        {"op": "add", "path": "/questions/-", "value": q2},
        {"op": "add", "path": "/questions/-", "value": q3},
        {"op": "add", "path": "/questions/-", "value": q4},
    ]
    r = httpx.patch(f"http://localhost:8001/editor/quiz/{quiz_get['_id']}", json=patch_request, headers=u1_auth,)
    r.raise_for_status()
    print(r.json())


if __name__ == "__main__":
    test_quiz()
# fmt: on
