import os
from dataclasses import dataclass
from fasthtml.common import *
from pb import get_pb
from pocketbase.utils import ClientResponseError


DEBUG = os.getenv("DEBUG", "false").lower() == "true"


# Status code 303 is a redirect that can change POST to GET,
# so it's appropriate for a login page.
login_redirect = RedirectResponse("/login", status_code=303)


def user_auth_before(request, session):
    # The `auth` key in the request scope is automatically provided
    # to any handler which requests it, and can not be injected
    # by the user using query params, cookies, etc, so it should
    # be secure to use.
    auth = request.scope["auth"] = session.get("auth")
    # If the session key is not there, it redirects to the login page.
    if not auth:
        return login_redirect


beforeware = Beforeware(
    user_auth_before,
    skip=[r"/favicon\.ico", r"/static/.*", r".*\.css", r".*\.js", "/login"],
)


app, rt = fast_app(live=DEBUG, debug=DEBUG, before=beforeware)


@rt("/")
def get(session):
    user = get_pb(session).auth_store.model
    print(f"Logged in as {user.email}")

    debug_out = f"""
id: {user.id}
name: {user.name}
email: {user.email}
email_visibility: {user.email_visibility}
avatar: {user.avatar}
updated: {user.updated}
created: {user.created}"""
    content = Pre(debug_out, style="padding:1rem;")

    top_nav = Grid(
        H1("Protected"),
        Div(
            "You are logged in as",
            Strong(user.email),
            NotStr("&sdot;"),
            A("Logout", href="/logout"),
            style="text-align: right;",
        ),
    )

    return Container(top_nav, Div(content))


@rt("/login")
def get(session):
    form = Form(
        # `name` attribute will be auto-set to the same as `id` if not provided
        Input(id="email", type="email", placeholder="Email"),
        Input(id="password", type="password", placeholder="Password"),
        Button("Login"),
        action="/login",
        method="post",
    )
    error = session.pop("error", None)
    error_div = Div(error, style="color: red;") if error else None
    return Container(H1("Login"), error_div, Div(form))


@dataclass
class LoginCredentials:
    email: str
    password: str


@rt("/login")
def post(creds: LoginCredentials, session):
    """
    This handler is called when a POST request is made to the `/login` path.

    The `creds` argument is an instance of the `LoginCredentials` class, which
    has been auto-instantiated from the form data.
    """
    if not creds.email or not creds.password:
        return login_redirect

    # Authenticate the user using the users collection.
    users_collection = get_pb(session).collection("users")

    try:
        resp = users_collection.auth_with_password(creds.email, creds.password)
    except ClientResponseError as e:
        session["error"] = e.data.get("message")
        return login_redirect
    else:
        if resp.is_valid:
            return RedirectResponse("/", status_code=303)

    return login_redirect


@rt("/logout")
def get(session):
    get_pb(session).auth_store.clear()
    return login_redirect


serve()
