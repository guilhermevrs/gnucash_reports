import pytest
from components.base_block import BaseBlock, BaseBlockConfig
from unittest.mock import patch, MagicMock


class ChildClass(BaseBlock):
    def callbacks():
        pass


class TestBaseBlock:

    @pytest.fixture(autouse=True)
    def before_each(self):
        """Fixture to execute asserts before and after a test is run"""
        # Setup
        yield  # this is where the testing happens
        # Teardown

    def test_empty_constructor(self):
        """should work with empty constructor"""
        baseBlock = BaseBlock()
        assert baseBlock is not None

    @patch('dash.Dash')
    def test_pass_app_to_constructor(self, MockDash: MagicMock):
        """should correctly assign the app if passed to constructor"""
        mockApp = MockDash()
        baseBlock = BaseBlock(app=mockApp)
        assert baseBlock.app == mockApp

    @patch.object(ChildClass, "callbacks")
    @patch("dash.Dash")
    def test_call_callbacks_when_needed(self, MockDash: MagicMock, mock_callback: MagicMock):
        """should call the callbacks method when exists and app is defined"""
        mockApp = MockDash()
        ChildClass(app=mockApp)
        mock_callback.assert_called_once()

    @patch.object(ChildClass, "callbacks")
    def test_no_call_callbacks_when_no_app(self, mock_callback: MagicMock):
        """should call the callbacks method when exists and app is defined"""
        ChildClass()
        mock_callback.assert_not_called()

    def test_pass_config_to_constructor(self):
        """should correctly assign the app if passed to constructor"""
        config = BaseBlockConfig(prefix="test")
        baseBlock = BaseBlock(config=config)
        assert baseBlock.config == config

    def test_prefix(self):
        config = BaseBlockConfig(prefix="myprefix")
        baseBlock = BaseBlock(config=config)
        assert baseBlock.prefix("component") == "myprefix-component"

    def test_prefix_name_when_no_config(self):
        baseBlock = BaseBlock()
        assert baseBlock.prefix("component") == "component"
