import datetime
import time
import typing

from urllib.parse import urljoin

import requests

IOS_CLIENT_ID = "13bcd503-2137-9085-a437-d9f2ac9281a1"


class TinybeansUser(object):
    def __init__(self, data: dict) -> None:
        self.id = data["id"]
        self.email_address = data["emailAddress"]
        self.first_name = data["firstName"]
        self.last_name = data["lastName"]
        self.username = data["username"]


class TinybeanFollowing(object):
    def __init__(self, data: dict) -> None:
        self.id = data["id"]
        self.url = data["URL"]
        self.relationship = data["relationship"]["label"]
        self.journal = TinybeanJournal(data["journal"])


class TinybeanJournal(object):
    def __init__(self, data: dict) -> None:
        self.id = data["id"]
        self.title = data["title"]
        self.children: typing.List[TinybeanChild] = []

        for child in data["children"]:
            self.children.append(TinybeanChild(journal=self, data=child))


class TinybeanChild(object):
    def __init__(self, journal: TinybeanJournal, data: dict) -> None:
        self.id = data["id"]
        self.first_name = data["firstName"]
        self.last_name = data["lastName"]
        self.gender = data["gender"]
        self.date_of_birth = datetime.datetime.strptime(data["dob"], "%Y-%m-%d")
        self.journal = journal

    def __repr__(self) -> str:
        return "<{name} {dob}>".format(
            name=self.name,
            dob=self.date_of_birth,
        )

    @property
    def name(self):
        return "%s %s" % (self.first_name, self.last_name)


class TinybeanEntry(object):
    def __init__(self, data: dict) -> None:
        self._data = data
        self.id = data["id"]
        self.uuid = data["uuid"]

        if data.get("attachmentType") == "VIDEO":
            self.type = "VIDEO"
            self.video_url = data["attachmentUrl_mp4"]
        else:
            self.type = data["type"]

        try:
            self.latitude = data["latitude"]
            self.longitude = data["longitude"]
        except KeyError:
            self.latitude = None
            self.longitude = None

        self.caption = data["caption"]
        self.blobs = data["blobs"]
        self.emotions: typing.List[TinybeanEmotion] = []

        try:
            for emotion in data["emotions"]:
                self.emotions.append(TinybeanEmotion(emotion))
        except KeyError:
            pass

        self.comments: typing.List[TinybeanComment] = []

        try:
            for comment in data["comments"]:
                self.comments.append(TinybeanComment(comment))
        except KeyError:
            pass


class TinybeanComment(object):
    def __init__(self, data: dict) -> None:
        self.id = data["id"]
        self.text = data["details"]
        self.user = TinybeansUser(data["user"])


class TinybeanEmotion(object):
    def __init__(self, data: dict) -> None:
        self.id = data["id"]
        self.entry_id = data["entryId"]
        self.user_id = data["userId"]
        self.type = data["type"]["label"]


class PyTinybeans(object):
    API_BASE_URL = "https://tinybeans.com/api/1/"
    CLIENT_ID = IOS_CLIENT_ID

    def __init__(self) -> None:
        self.session = requests.Session()
        self._access_token = None

    def _api(
        self, path: str, params: dict = None, json: dict = None, method: str = "GET"
    ) -> requests.Response:
        url = urljoin(self.API_BASE_URL, path)

        if self._access_token:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json,
                headers={"authorization": self._access_token},
            )
        else:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json,
            )

        return response

    @property
    def logged_in(self):
        if self._access_token:
            return True

        return False

    def login(self, username: str, password: str) -> None:
        if self.logged_in:
            # check via api/me or something that this token works
            return

        response = self._api(
            path="authenticate",
            json={
                "username": username,
                "password": password,
                "clientId": IOS_CLIENT_ID,
            },
            method="POST",
        )

        self._access_token = response.json()["accessToken"]
        self.user = TinybeansUser(data=response.json()["user"])

    def get_followings(self):
        response = self._api(
            path="followings",
            params={"clientId": self.CLIENT_ID},
        )

        for following in response.json()["followings"]:
            yield TinybeanFollowing(following)

    @property
    def children(self):
        children = []
        for following in self.get_followings():
            children.extend(following.journal.children)

        return children

    def get_entries(self, child: TinybeanChild, last: int = None):
        entries = []

        if last is None:
            last = int(
                time.mktime(
                    (
                        datetime.datetime.utcnow() - datetime.timedelta(days=0)
                    ).timetuple()
                )
                * 1000
            )

        response = self._api(
            path="journals/%s/entries" % child.journal.id,
            params={
                "clientId": self.CLIENT_ID,
                "fetchSize": 200,
                "last": last,
            },
        )

        for entry in response.json()["entries"]:
            entries.append(TinybeanEntry(entry))

        while response.json()["numEntriesRemaining"] > 0:
            last = response.json()["entries"][0]["timestamp"]

            response = self._api(
                path="journals/%s/entries" % child.journal.id,
                params={
                    "clientId": self.CLIENT_ID,
                    "fetchSize": 200,
                    "last": last,
                },
            )

            for entry in response.json()["entries"]:
                entries.append(TinybeanEntry(entry))

        return entries

    def request_export(
        self, journal: TinybeanJournal, start_dt: datetime, end_dt: datetime
    ) -> bool:
        response = self._api(
            method="POST",
            path="/api/1/journals/{journal_id}/export".format(journal_id=journal.id),
            params={
                "startDate": start_dt.strftime("%Y-%m-%d"),
                "endDate": end_dt.strftime("%Y-%m-%d"),
            },
        )

        if response.json()["status"] == "ok":
            return True

        return False
