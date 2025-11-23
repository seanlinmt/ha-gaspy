import sys
from unittest.mock import MagicMock

# Mock Home Assistant modules
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.config_entries"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.const"] = MagicMock()
sys.modules["homeassistant.exceptions"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
# sys.modules["homeassistant.helpers.entity"] = MagicMock() # Don't mock the whole module yet


# Define a dummy Entity class
class Entity:
    @property
    def unique_id(self):
        return self._unique_id


mock_entity_module = MagicMock()
mock_entity_module.Entity = Entity
sys.modules["homeassistant.helpers.entity"] = mock_entity_module

sys.modules["homeassistant.helpers.config_validation"] = MagicMock()
sys.modules["homeassistant.components"] = MagicMock()
sys.modules["homeassistant.components.sensor"] = MagicMock()

# Mock requests
sys.modules["requests"] = MagicMock()
sys.modules["requests"].codes.ok = 200

# Mock voluptuous
sys.modules["voluptuous"] = MagicMock()

# Mock specific constants used
sys.modules["homeassistant.const"].CONF_USERNAME = "username"
sys.modules["homeassistant.const"].CONF_PASSWORD = "password"
sys.modules["homeassistant.const"].CONF_LATITUDE = "latitude"
sys.modules["homeassistant.const"].CONF_LONGITUDE = "longitude"

# Import the code to verify syntax and basic logic
from custom_components.gaspy.api import GaspyApi
from custom_components.gaspy.sensor import GaspyFuelPriceSensor
from custom_components.gaspy.const import DOMAIN


def test_api_login_state():
    print("Testing API login state...")
    api = GaspyApi("user", "pass", 10, 1.0, 2.0)
    assert api.is_logged_in is False, "Should not be logged in initially"

    # Mock session
    api._session = MagicMock()

    # Mock successful login
    mock_response = MagicMock()
    mock_response.status_code = 200
    api._session.get.return_value = mock_response
    api._session.post.return_value = mock_response

    result = api.login()
    assert result is True, "Login should succeed"
    assert api.is_logged_in is True, "Should be logged in after success"
    print("API login state test passed!")


def test_sensor_unique_id():
    print("Testing Sensor Unique ID...")
    api = GaspyApi("user", "pass", 10, 1.23, 4.56)
    sensor = GaspyFuelPriceSensor("Gaspy Sensor", api)

    expected_id = f"{DOMAIN}_1.23_4.56"
    assert sensor.unique_id == expected_id, (
        f"Expected {expected_id}, got {sensor.unique_id}"
    )
    print("Sensor Unique ID test passed!")


def test_sensor_update_logic():
    print("Testing Sensor Update Logic...")
    api = GaspyApi("user", "pass", 10, 1.0, 2.0)
    api.login = MagicMock(return_value=True)
    api.get_prices = MagicMock(return_value={"data": []})

    sensor = GaspyFuelPriceSensor("Gaspy Sensor", api)

    # First update, should call login
    sensor.update()
    api.login.assert_called_once()

    # Manually set logged in state (since our mock didn't set the real flag because we mocked the method)
    api._is_logged_in = True
    api.login.reset_mock()

    # Second update, should NOT call login because is_logged_in is True
    sensor.update()
    api.login.assert_not_called()
    print("Sensor Update Logic test passed!")


if __name__ == "__main__":
    try:
        test_api_login_state()
        test_sensor_unique_id()
        test_sensor_update_logic()
        print("\nAll verification tests passed!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        sys.exit(1)
