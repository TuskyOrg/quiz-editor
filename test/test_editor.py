# Another case of poor testing 🙁
# Oh well, at least there's something
# fmt: off
import json

import httpx
from httpx import HTTPStatusError

from common import u1, u1_auth, u2, u2_auth


def test_editor():
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
    assert r.is_error, f"Oh no! A user gave another user a quiz without their permission! (probably), `{r.content}`"

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
    r = httpx.patch(f"http://localhost:8001/editor/quiz/{quiz_get['_id']}", json=patch_request, headers=u1_auth)
    r.raise_for_status()

    ####################################################################################
    # Assert delete fails without auth
    r = httpx.delete(f"http://localhost:8001/editor/quiz", params={"id": quiz_get['_id']})
    assert r.status_code == 403, f"Something went wrong during deletion. `{r.content}`"

    ####################################################################################
    # Assert delete works
    r = httpx.delete(f"http://localhost:8001/editor/quiz/", headers=u1_auth, params={"id": quiz_get['_id']})
    r.raise_for_status()
    r = httpx.get(f"http://localhost:8001/editor/quiz/", headers=u1_auth, params={"id": quiz_get['_id']})
    if r.status_code != 404:
        raise ValueError("The object wasn't deleted. ", r.content)


if __name__ == "__main__":
    test_editor()
# fmt: on