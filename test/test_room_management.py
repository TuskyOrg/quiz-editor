# TESTS ARE CURRENTLY FAILING
# fmt: off
import httpx

from common import u1, u1_auth, u2, u2_auth


def test_room_management():
    # Assert room can be created
    r = httpx.post("http://localhost:8001/room-management", headers=u1_auth, json={"code": "ABCDE", "owner": u1.id, "is_active": True})
    assert not r.is_error, f"{r.status_code}, {r.content}"
    room1_info = r.json()
    print(r.json())

    # Assert room can not be created for someone else
    r = httpx.post("http://localhost:8001/room-management", headers=u2_auth, json={"code": "LMNOP", "owner": u1.id, "is_active": True})
    assert r.status_code == 403, f"{r.status_code}, {r.content}"

    # Assert the same room can't be created twice while active
    r = httpx.post("http://localhost:8001/room-management", headers=u1_auth, json={"code": "ABCDE", "owner": u1.id, "is_active": True})
    assert r.is_error, r.content

    # Todo:
    #  Assert you can actually get the room

    # Assert closing room
    r = httpx.post(f"http://localhost:8001/room-management/{room1_info['id']}/close")
    assert r.status_code == 204, f"{r.status_code}, {r.content}"

    # Assert new room with same code can now be activated
    r = httpx.post("http://localhost:8001/room-management", headers=u1_auth, json={"code": "ABCDE", "owner": u1.id, "is_active": True})
    assert not r.is_error, f"{r.status_code}, {r.content}"


if __name__ == '__main__':
    test_room_management()

# fmt: on
