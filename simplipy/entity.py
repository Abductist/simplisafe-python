"""Define a base SimpliSafe entity."""
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, cast

if TYPE_CHECKING:
    from simplipy.api import API
    from simplipy.system import System


class EntityTypes(Enum):
    """Entity types based on internal SimpliSafe ID number."""

    remote = 0
    keypad = 1
    keychain = 2
    panic_button = 3
    motion = 4
    entry = 5
    glass_break = 6
    carbon_monoxide = 7
    smoke = 8
    leak = 9
    temperature = 10
    camera = 12
    siren = 13
    doorbell = 15
    lock = 16
    lock_keypad = 253
    unknown = 99


class Entity:
    """A base SimpliSafe entity.

    Note that this class shouldn't be instantiated directly; it will be instantiated as
    appropriate via :meth:`simplipy.API.get_systems`.

    :param request: A method to make authenticated API requests.
    :type request: ``Callable[..., Coroutine]``
    :param update_func: A method to update the entity.
    :type update_func: ``Callable[..., Coroutine]``
    :param system_id: A SimpliSafe system ID.
    :type system_id: ``int``
    :param entity_type: The type of entity that this object represents.
    :type entity_type: ``simplipy.entity.EntityTypes``
    :param entity_data: A raw data dict representing the entity's state and properties.
    :type entity_data: ``dict``
    """

    def __init__(
        self, api: "API", system: "System", entity_type: EntityTypes, serial: str
    ) -> None:
        """Initialize."""
        self._api = api
        self._entity_type = entity_type
        self._serial = serial
        self._system = system

    @property
    def name(self) -> str:
        """Return the entity name.

        :rtype: ``str``
        """
        return cast(str, self._system.entity_data[self._serial]["name"])

    @property
    def serial(self) -> str:
        """Return the entity's serial number.

        :rtype: ``str``
        """
        return cast(str, self._system.entity_data[self._serial]["serial"])

    @property
    def type(self) -> EntityTypes:
        """Return the entity type.

        :rtype: :meth:`simplipy.entity.EntityTypes`
        """
        return self._entity_type

    async def update(self, cached: bool = True) -> None:
        """Retrieve the latest state/properties for the entity.

        The ``cached`` parameter determines whether the SimpliSafe Cloud uses the last
        known values retrieved from the base station (``True``) or retrieves new data.

        :param cached: Whether to used cached data.
        :type cached: ``bool``
        """
        await self._system.update(
            include_system=False, include_settings=False, cached=cached
        )


class EntityV3(Entity):
    """A base entity for V3 systems.

    Note that this class shouldn't be instantiated directly; it will be
    instantiated as appropriate via :meth:`simplipy.API.get_systems`.
    """

    @property
    def error(self) -> bool:
        """Return the entity's error status.

        :rtype: ``bool``
        """
        return cast(
            bool,
            self._system.entity_data[self._serial]["status"].get("malfunction", False),
        )

    @property
    def low_battery(self) -> bool:
        """Return whether the entity's battery is low.

        :rtype: ``bool``
        """
        return cast(bool, self._system.entity_data[self._serial]["flags"]["lowBattery"])

    @property
    def offline(self) -> bool:
        """Return whether the entity is offline.

        :rtype: ``bool``
        """
        return cast(bool, self._system.entity_data[self._serial]["flags"]["offline"])

    @property
    def settings(self) -> Dict[str, Any]:
        """Return the entity's settings.

        Note that these can change based on what entity type the entity is.

        :rtype: ``dict``
        """
        return cast(Dict[str, Any], self._system.entity_data[self._serial]["setting"])
