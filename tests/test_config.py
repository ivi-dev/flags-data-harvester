import unittest
from unittest.mock import mock_open, patch
import main


mock_dbname = "countries"
mock_data_url = "https://example.com"
mock_config = '{"key": "val"}'


def mock_environ(key, *args):
    if key == f"{main.CONFIG_ENVIRON_PREFIX}DB_NAME":
        return mock_dbname
    elif key == f"{main.CONFIG_ENVIRON_PREFIX}DATAURL":
        return mock_data_url
    else:
        raise ValueError(
            f"\"{key}\" is not a valid key "
            "for the mock environment."
        )


class ConfigTest(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data=mock_config)
    def test_try_load_config_loads_a_valid_json_config(self, mock_open):
        config = main.try_load_config()
        self.assertEqual({"key": "val"}, config)

    @patch("main.config", None)
    @patch("os.environ.get", new=mock_environ)
    def test_get_config_value_returns_top_level_value_when_config_file_is_missing(self):
        val = main.get_config_value("dataUrl")
        self.assertEqual(mock_data_url, val)

    @patch("main.config", None)
    @patch("os.environ.get", new=mock_environ)
    def test_get_config_value_returns_nested_value_when_config_file_is_missing(self):
        val = main.get_config_value("db.name")
        self.assertEqual(mock_dbname, val)