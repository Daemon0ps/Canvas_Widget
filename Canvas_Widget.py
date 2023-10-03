import PySimpleGUI as sg
import sys
import requests
from requests import Response, ConnectionError
from requests.adapters import HTTPAdapter, Retry
import keyring
import json
from datetime import datetime, timezone
from dataclasses import dataclass
from dateutil.parser import parse


@dataclass(frozen=True)
class win:
    dow: sg.Window

    def __post_init__(self):
        self.dow = win.dow
        super().__setattr__("attr_name", self)


@dataclass(frozen=False)
class c:
    token: str = keyring.get_password("canvas", "api_token")
    url0: str = keyring.get_password("canvas", "endpoint")
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=5)
    adapter = HTTPAdapter(max_retries=30)
    cxn_state: bool = False
    ld = {}
    _ld = lambda x: {c.ld[k]: v for k, v in dict(x).items()}
    _lh = lambda x: list([dict(x)[k]["url"] for k, v in dict(x).items()])
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json+canvas-string-ids",
    }
    data = {
        "courses": [],
        "assignments": [],
        "calendar_events": [],
    }
    class_list = []
    class_list_names = []
    assignments = []
    assignments_names = []
    events = []
    loc: tuple = ()

    def __post_init__(self):
        self.cxn_state = c.cxn_state
        self.url0 = c.url0
        self.token = c.token
        self.headers = c.headers
        self.courses = c.courses
        self.assignments = c.assignments
        self.calendar_events = c.calendar_events
        self.ld = c.ld
        self.data = c.data
        self.class_list = c.class_list
        self.class_list_names = c.class_list_names
        self.assignments = c.assignments
        self.assignments_names = c.assignments_names
        self.events = c.events
        self.missing_submissions = c.missing_submissions
        super().__setattr__("attr_name", self)

    @staticmethod
    def _cxn() -> requests.Session:
        if c.cxn_state:
            try:
                c.session.close()
                c.cxn_state = False
            except Exception as cxe:
                pass
        c.session = requests.Session()
        c.retry = Retry(connect=3, backoff_factor=5)
        c.adapter = HTTPAdapter(max_retries=30)
        c.session.mount("https://", c.adapter)
        c.cxn_state = True
        return c.session

    @staticmethod
    def _get(ep: str) -> list[Response]:
        resp_list: list[Response] = []
        link_headers: list[str] = []
        try:
            c.session = c._cxn()
            resp = c.session.get(ep, headers=c.headers)
            if len(resp.links) == 0:
                resp_list.append(resp)
                return resp_list
            if resp is not None:
                resp_list.append(resp)
                link_headers = c._lh(resp.links)
                while link_headers[0] != link_headers[3]:
                    if link_headers[0] != link_headers[1]:
                        resp = c.session.get(link_headers[1], headers=c.headers)
                        resp_list.append(resp)
                        link_headers = c._lh(resp.links)
                    else:
                        break
            c.session.close()
            c.cxn_state = False
            return resp_list
        except KeyboardInterrupt:
            sys.exit()
        except ConnectionError as ce:
            pass
        except Exception as e:
            pass

    @staticmethod
    def curr_term_class_list() -> None:
        curr_term_id: int = int(0)
        top_curr_term = c.data["courses"].index(
            sorted(c.data["courses"], key=lambda x: x["id"], reverse=True)[:1][0]
        )
        curr_term_id = str(c.data["courses"][top_curr_term]["account_id"])
        c.class_list = []
        c.class_list = [x for x in c.data["courses"] if x["account_id"] == curr_term_id]
        c.class_list_names = [x["name"] for x in c.class_list]

    @staticmethod
    def _init_classes() -> None:
        c.data["courses"] = []
        resps = c._get(f"{c.url0}users/self/courses")
        for resp in resps:
            jobj = json.loads(resp.text)
            for d in jobj:
                c.data["courses"].append(d)

    @staticmethod
    def _init_calendar() -> None:
        c.data["calendar_events"] = []
        resps = c._get(f"{c.url0}users/self/upcoming_events")
        if resps is not None:
            for resp in resps:
                jobj = json.loads(resp.text)
                for d in jobj:
                    c.data["calendar_events"].append(d)

    @staticmethod
    def _init_assignments() -> None:
        c.data["assignments"] = []
        for course in c.class_list:
            resps = c._get(f'{c.url0}courses/{course["id"]}/assignments')
            if resps is not None:
                for resp in resps:
                    jobj = json.loads(resp.text)
                    for d in jobj:
                        c.data["assignments"].append(d)
        if len(c.data["assignments"]) > 0:
            c.assignments = [x for x in c.data["assignments"]]
            c.assignments_names = [x["name"] for x in c.assignments]

    @staticmethod
    def dt_p(d: str) -> datetime:
        return datetime.combine(
            parse(d).date(), parse(d).time(), tzinfo=parse(d).tzinfo
        )

    @staticmethod
    def t_s(i: int) -> dict:
        x0 = int(i)
        xD = str(x0 // 86400).zfill(2)
        xH = str(x0 % 86400 // 3600).zfill(2)
        xM = str(x0 % 86400 % 3600 // 60).zfill(2)
        xS = str((((x0 % 86400) % 3600) % 60)).zfill(2)
        return {"d": f"{xD}", "h": f"{xH}", "m": f"{xM}", "s": {xS}}

    @staticmethod
    def _get_token() -> None:
        api_key = ""
        endpoint = ""

        def api_check(endpoint: str, api_key: str) -> bool:
            key_check = False
            head_check = {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json+canvas-string-ids",
            }
            c.headers = head_check
            try:
                resps = c._get(f"{endpoint}users/self/courses")
                resp = json.loads(resps[0].text)
                try:
                    if resp["errors"][0]["message"]:
                        key_check = False
                        sg.popup("Invalid Token", title="Invalid Token")
                except TypeError as e:
                    if len(resp) > 1:
                        kc = resp[0]
                        if kc["id"]:
                            key_check = True
                            return key_check, api_key, endpoint
                except KeyError as e:
                    sg.popup_error_with_traceback("Invalid Key", e)
                except Exception as e:
                    sg.popup_error_with_traceback("NaN. Qwatz?!", e)
                if resps[0].text.find("Invalid access token.") != -1:
                    sg.popup("Invalid Token", title="Invalid Token")
                    key_check = False
            except Exception as e:
                sg.popup_error_with_traceback("NaN. Qwatz?!", e)
            return key_check, api_key, endpoint

        layout = [
            [
                sg.Text(
                    f"Please enter API Key",
                    background_color="#000000",
                    text_color="#6495ED",
                    pad=0,
                    font="Consolas 10",
                ),
                sg.Input(
                    "",
                    background_color="#000000",
                    text_color="#00FFFF",
                    pad=0,
                    font="Consolas 10",
                    key="-APIKEY-",
                ),
            ],
            [
                sg.Text(
                    f"Please enter EndPoint Address",
                    background_color="#000000",
                    text_color="#6495ED",
                    pad=0,
                    font="Consolas 10",
                ),
                sg.Input(
                    "",
                    background_color="#000000",
                    text_color="#00FFFF",
                    pad=0,
                    font="Consolas 10",
                    key="-ENDPOINT-",
                ),
            ],
            [
                sg.Button(
                    button_text="Submit",
                    enable_events=True,
                    button_color="#323232",
                    key="-SUBMIT-",
                ),
            ],
        ]

        api_window = sg.Window(
            "Enter API Key",
            layout,
            font="Consolas 10",
            background_color="#000000",
            use_custom_titlebar=False,
            titlebar_background_color="#000000",
            titlebar_text_color="#ffffff",
            keep_on_top=False,
            grab_anywhere=True,
            use_default_focus=False,
            finalize=True,
        )

        api_window["-APIKEY-"].Widget.config(insertbackground="red")

        while True:
            event, values = api_window.read(timeout=120000)
            if event == "-SUBMIT-":
                endpoint = str(values["-ENDPOINT-"]).lower().replace("http:", "https:")
                if endpoint[:1] != "/":
                    endpoint = endpoint + "/"
                if endpoint[-5:] != "https":
                    endpoint = "https" + endpoint
                api_key = values["-APIKEY-"]
                key_check, api_key, endpoint = api_check(endpoint, api_key)
                if key_check:
                    keyring.set_password("canvas", "api_token", f"{api_key}")
                    keyring.set_password("canvas", "endpoint", f"{endpoint}")
                    c.token = keyring.get_password("canvas", "api_token")
                    c.url0 = keyring.get_password("canvas", "endpoint")
                    sg.popup("SUCCESS", title="SUCCESS")
                    break
                else:
                    api_window["-APIKEY-"].Update("")
                    continue
            if event == sg.WIN_CLOSED:
                break
            if event == "Exit":
                break
        api_window.close()


def mk_win(loc: tuple = ()) -> sg.Window:
    sg.theme("Dark Blue")
    assignment_layout = []
    assignment_lengths = sorted(
        [len(str(x["name"]).strip()) for x in c.data["assignments"]], reverse=True
    )
    print(f"AssnLen: ", assignment_lengths)
    for assignment in sorted(
        c.data["assignments"], key=lambda x: x["due_at"], reverse=False
    ):
        if assignment["has_submitted_submissions"] == False:
            assn_dt = c.dt_p(assignment["due_at"])
            dt = datetime.now(timezone.utc) - assn_dt
            dd = c.t_s(dt.total_seconds())
            assn_data = [
                [
                    sg.Text(
                        f'{dd["d"]}',
                        background_color="#000000",
                        text_color="#FF8C00",
                        pad=0,
                        font="Consolas 10",
                    ),
                    sg.Text(
                        f" Days",
                        background_color="#000000",
                        text_color="#6495ED",
                        pad=0,
                        font="Consolas 10",
                    ),
                    sg.Text(
                        f'{dd["h"]}',
                        background_color="#000000",
                        text_color="#FF8C00",
                        pad=0,
                        font="Consolas 10",
                    ),
                    sg.Text(
                        f" Hours",
                        background_color="#000000",
                        text_color="#6495ED",
                        pad=0,
                        font="Consolas 10",
                    ),
                    sg.Text(
                        f'{dd["m"]}',
                        background_color="#000000",
                        text_color="#FF8C00",
                        pad=0,
                        font="Consolas 10",
                    ),
                    sg.Text(
                        f" Minutes",
                        background_color="#000000",
                        text_color="#6495ED",
                        pad=0,
                        font="Consolas 10",
                    ),
                ]
            ]
            assignment_layout.append(
                [
                    sg.Frame(
                        f'{assignment["name"]}',
                        layout=assn_data,
                        background_color="#000000",
                        font="Consolas 10",
                        title_color="#87CEEB",
                        vertical_alignment="top",
                        size=(assignment_lengths[0] * 8, 40),
                    ),
                ]
            )

    calendar_layout = []
    title_lengths = sorted(
        [len(str(x["title"]).strip()) for x in c.data["calendar_events"]], reverse=True
    )
    print(f"title_lens: ", title_lengths)
    for event in sorted(
        c.data["calendar_events"], key=lambda x: x["all_day_date"], reverse=False
    ):
        cal_data = [
            [
                sg.Text(
                    f'{event["title"]}',
                    background_color="#000000",
                    text_color="#6495ED",
                    pad=0,
                    font="Consolas 10",
                ),
            ],
        ]
        calendar_layout.append(
            [
                sg.Frame(
                    f'{event["all_day_date"]}',
                    layout=cal_data,
                    background_color="#000000",
                    font="Consolas 10",
                    title_color="#FF8C00",
                    vertical_alignment="top",
                    size=(title_lengths[0] * 8, 40),
                ),
            ],
        )

    frame_layout = [
        [
            sg.Frame(
                "Assignments",
                layout=assignment_layout,
                background_color="#000000",
                font="Consolas 10",
                title_color="#FFA500",
                vertical_alignment="top",
            ),
        ],
        [sg.Text("")],
        [
            sg.Frame(
                "Calendar Events",
                layout=calendar_layout,
                background_color="#000000",
                font="Consolas 10",
                title_color="#FFA500",
                vertical_alignment="top",
            ),
        ],
    ]

    sg.set_options(text_justification="left")

    return sg.Window(
        "Image Tagger",
        frame_layout,
        font="Consolas 10",
        background_color="#000000",
        use_custom_titlebar=False,
        titlebar_background_color="#000000",
        titlebar_text_color="#ffffff",
        keep_on_top=True,
        grab_anywhere=True,
        no_titlebar=True,
        use_default_focus=False,
        right_click_menu=sg.MENU_RIGHT_CLICK_EXIT,
        finalize=True,
        location=(0, 0) if loc == () else loc,
    )


def init_win() -> None:
    win.dow = mk_win()
    while True:
        event, values = win.dow.read(timeout=900000)
        if event == sg.WIN_CLOSED:
            break
        if event == "Exit":
            break
        if event == "__TIMEOUT__":
            location = win.dow.current_location()
            c._init_classes()
            c.curr_term_class_list()
            c._init_calendar()
            c._init_assignments()
            win.dow.close()
            win.dow = mk_win(location)
    win.dow.close()
    sys.exit()


if __name__ == "__main__":
    if c.token == None or c.url0 == "":
        c._get_token()
    c._init_classes()
    c.curr_term_class_list()
    c._init_calendar()
    c._init_assignments()
    init_win()
