import os
from datetime import datetime
from typing import Any, Dict
from pocketbase import PocketBase
from pocketbase.stores.base_auth_store import BaseAuthStore
from pocketbase.models.record import Record
from pocketbase.models.admin import Admin


PB_BASE_URL = os.getenv("PB_BASE_URL", "http://localhost:8090")


class PocketBaseAuthStore(BaseAuthStore):

    def __init__(
        self,
        session: Dict[str, Any],
        base_token: str = "",
        base_model: Record | Admin | None = None,
    ) -> None:
        super().__init__(base_token, base_model or Record())
        self.session = session

    @property
    def token(self) -> str | None:
        return self.session.get("auth")

    @property
    def model(self) -> Record | Admin | None:
        """
        Create a model class from the stored session data.
        """
        auth_model = self.session.get("auth_model")

        if not auth_model or not self.base_model:
            return None

        # Avoid mutating the session data
        _model_data = auth_model.copy()

        # Populate the base model with the user data
        self.base_model.load(_model_data)

        return self.base_model

    def save(self, token: str = "", model: Record | Admin | None = None) -> None:
        """
        Store the PocketBase token and a serializable representation of the model in
        the session.
        """
        self.session["auth"] = token
        self.session["auth_model"] = {
            "id": model.id,
            "collection_id": model.collection_id,
            "collection_name": model.collection_name,
            "username": model.username,
            "verified": model.verified,
            "email_visibility": model.email_visibility,
            "email": model.email,
            "created": self._dt_to_str(model.created),
            "updated": self._dt_to_str(model.updated),
            "name": model.name,
            "avatar": model.avatar,
        }
        super().save(token, model)

    def clear(self) -> None:
        del self.session["auth"]
        del self.session["auth_model"]
        super().clear()

    def _dt_to_str(self, dt: datetime, format="%Y-%m-%d %H:%M:%S") -> str:
        return datetime.strftime(dt, format)


def get_pb(session: Dict[str, Any]):
    return PocketBase(PB_BASE_URL, auth_store=PocketBaseAuthStore(session))
