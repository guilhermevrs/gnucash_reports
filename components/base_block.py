

from dataclasses import dataclass
from dash.dash import Dash
from dash.development.base_component import Component


@dataclass
class BaseBlockConfig:
    prefix: str


class BaseBlock:
    """
    Defines a base component block for Dash
    """

    app: Dash
    config: BaseBlockConfig
    layout: Component

    def __init__(self, app: Dash = None, config: BaseBlockConfig = None) -> None:
        self.app = app
        self.config = config

        if self.app is not None and hasattr(self, "callbacks"):
            self.callbacks()

    def get_prefixed_name(self, name: str) -> str:
        """returns a prefixed name based on config"""
        return "{}-{}".format(self.config.prefix, name) if self.config is not None else name
