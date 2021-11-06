

from dataclasses import dataclass
from dash.dash import Dash
from dash.development.base_component import Component


@dataclass
class BaseComponentConfig:
    prefix: str


class BaseComponent:
    """
    Defines a base component block for Dash
    """

    app: Dash
    config: BaseComponentConfig
    layout: Component

    def __init__(self, app: Dash = None, config: BaseComponentConfig = None) -> None:
        self.app = app
        self.config = config

        self.layout = self.render()

        if self.app is not None and hasattr(self, "callbacks"):
            self.callbacks()

    def prefix(self, name: str) -> str:
        """returns a prefixed string based on config"""
        return "{}-{}".format(self.config.prefix, name) if hasattr(self, "config") and self.config is not None else name

    def render(self) -> Component:
        """returns the layout to be rendered by the component"""
        pass
