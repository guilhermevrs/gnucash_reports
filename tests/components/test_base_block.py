from dash.dash import Dash
import pytest
from components.base_block import BaseComponent, BaseComponentConfig
from unittest.mock import patch, MagicMock
from dash import html


class ChildClass(BaseComponent):
    def callbacks(self, app: Dash):
        pass


class TestBaseComponent:

    @pytest.fixture(autouse=True)
    def before_each(self):
        """Fixture to execute asserts before and after a test is run"""
        # Setup
        yield  # this is where the testing happens
        # Teardown

    def test_empty_constructor(self):
        """should work with empty constructor"""
        baseBlock = BaseComponent()
        assert baseBlock is not None

    @patch.object(ChildClass, "callbacks")
    @patch("dash.Dash")
    def test_call_callbacks_when_needed(self, MockDash: MagicMock, mock_callback: MagicMock):
        """should call the callbacks method when exists and app is defined"""
        mockApp = MockDash()
        ChildClass(app=mockApp)
        mock_callback.assert_called_with(app=mockApp)

    @patch.object(ChildClass, "callbacks")
    def test_no_call_callbacks_when_no_app(self, mock_callback: MagicMock):
        """should call the callbacks method when exists and app is defined"""
        ChildClass()
        mock_callback.assert_not_called()

    def test_pass_config_to_constructor(self):
        """should correctly assign the app if passed to constructor"""
        config = BaseComponentConfig(prefix="test")
        baseBlock = BaseComponent(config=config)
        assert baseBlock.config == config

    def test_prefix(self):
        """should correctly prefix with the configured prefix"""
        config = BaseComponentConfig(prefix="myprefix")
        baseBlock = BaseComponent(config=config)
        assert baseBlock.prefix("component") == "myprefix-component"

    def test_prefix_name_when_no_config(self):
        """should return the string as it is, since no config"""
        baseBlock = BaseComponent()
        assert baseBlock.prefix("component") == "component"

    def test_prefix_from_child_when_no_config(self):
        """should return the string as it is, since no config"""
        baseBlock = ChildClass()
        assert baseBlock.prefix("component") == "component"

    @patch.object(BaseComponent, "render")
    @patch("dash.Dash")
    def test_call_render_on_init(self, MockDash: MagicMock, mock_callback: MagicMock):
        """should call the render method on init"""
        expected = html.Div(children=["My Test"])
        mock_callback.return_value = expected

        mockApp = MockDash()
        c = BaseComponent(app=mockApp)
        mock_callback.assert_called_once()

        assert c.layout == expected


