"""Unit tests for ElectricVehicleCharger ECHONET device class."""
import unittest
from pychonet.ElectricVehicleCharger import ElectricVehicleCharger
from pychonet.EchonetInstance import call_epc_function
from pychonet.lib.epc import EPC_CODE


class MockECHONETAPIClient:
    """Mock API client for testing ElectricVehicleCharger functionality.

    Uses EOJX codes: group=0x02, class=0x7E (Electric vehicle charger/discharger)
    """

    def __init__(self):
        self._state = {
            "192.168.1.50": {
                "instances": {
                    0x02: {
                        0x7E: {
                            0x01: {
                                0x80: b"\x30",  # Operation status: on
                                0xC5: b"\x00\x00\x00\x64",  # Rated charge capacity (100 Wh)
                                0xC7: b"\x41",  # Connected to vehicle, Chargeable
                                0xCC: b"\x12",  # Charger type: AC_HLC (charging only)
                                0xD3: b"\x00\x00\x05\xF8",  # Instantaneous power (1520 W)
                                0xDA: b"\x44",  # Operating mode: Standby
                                0xE6: b"\x00\x32",  # Vehicle ID (50)
                                0x9F: [0x80, 0xC5, 0xC7, 0xD3, 0xDA, 0xE6],
                                0x9E: [0x80, 0xDA],
                            }
                        },
                    },
                },
            },
        }

    async def echonetMessage(
        self, host, eojgc, eojcc, eojci, message_type, opc
    ):
        """Simulate successful ECHONET message response."""
        return True


class TestClassCode(unittest.TestCase):
    """Verify the class uses 0x7E (charger/discharger), not 0xA1 (charger only)."""

    def test_eojcc_is_0x7E(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        self.assertEqual(charger._eojcc, 0x7E)

    def test_eojgc_is_0x02(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        self.assertEqual(charger._eojgc, 0x02)


class TestDAOperationMode(unittest.TestCase):
    """Test DA (0xDA) operation mode parsing with all valid modes."""

    def _parse_da(self, byte_val):
        epc_func = ElectricVehicleCharger.EPC_FUNCTIONS[0xDA]
        return call_epc_function(epc_func, byte_val)

    def test_da_charging(self):
        self.assertEqual(self._parse_da(b"\x42"), "Charging")

    def test_da_discharging(self):
        self.assertEqual(self._parse_da(b"\x43"), "Discharging")

    def test_da_standby(self):
        self.assertEqual(self._parse_da(b"\x44"), "Standby")

    def test_da_idle(self):
        self.assertEqual(self._parse_da(b"\x47"), "Idle")

    def test_da_other(self):
        self.assertEqual(self._parse_da(b"\x40"), "Other")


class TestEPCParsers(unittest.TestCase):
    """Test EPC_FUNCTIONS parsers for key EPCs."""

    def _parse(self, epc, byte_val):
        epc_func = ElectricVehicleCharger.EPC_FUNCTIONS[epc]
        return call_epc_function(epc_func, byte_val)

    # Existing EPCs
    def test_d3_signed_positive(self):
        """D3: instantaneous power, positive = charging (1528 W)."""
        self.assertEqual(self._parse(0xD3, b"\x00\x00\x05\xF8"), 1528)

    def test_d3_signed_negative(self):
        """D3: instantaneous power, negative = discharging (-3000 W)."""
        self.assertEqual(self._parse(0xD3, b"\xff\xff\xf4\x48"), -3000)

    def test_d8_cumulative_charge(self):
        """D8: cumulative charging energy (86400 Wh)."""
        self.assertEqual(self._parse(0xD8, b"\x00\x01\x51\x80"), 86400)

    def test_e4_soc(self):
        """E4: remaining stored electricity 3 (SoC 100%)."""
        self.assertEqual(self._parse(0xE4, b"\x64"), 100)

    def test_e2_remaining_electricity(self):
        """E2: remaining stored electricity 1 (20000 Wh)."""
        self.assertEqual(self._parse(0xE2, b"\x00\x00\x4e\x20"), 20000)

    def test_c7_connected_chargeable(self):
        """C7: vehicle connected and chargeable."""
        self.assertEqual(
            self._parse(0xC7, b"\x41"),
            "Connected to vehicle, Chargeable",
        )

    def test_c7_not_connected(self):
        """C7: vehicle not connected."""
        self.assertEqual(self._parse(0xC7, b"\x30"), "Vehicle not connected")

    def test_c7_dischargeable(self):
        """C7: vehicle connected, dischargeable only (not chargeable)."""
        self.assertEqual(
            self._parse(0xC7, b"\x42"),
            "Connected to vehicle, Dischargeable",
        )

    def test_c7_chargeable_and_dischargeable(self):
        """C7: vehicle connected, both chargeable and dischargeable."""
        self.assertEqual(
            self._parse(0xC7, b"\x43"),
            "Connected to vehicle, Chargeable and Dischargeable",
        )

    # New discharge EPCs
    def test_d6_cumulative_discharge(self):
        """D6: cumulative discharging energy (86400 Wh)."""
        self.assertEqual(self._parse(0xD6, b"\x00\x01\x51\x80"), 86400)

    def test_c0_dischargeable_capacity(self):
        """C0: dischargeable capacity 1 (20000 Wh)."""
        self.assertEqual(self._parse(0xC0, b"\x00\x00\x4e\x20"), 20000)

    def test_c4_remaining_dischargeable_pct(self):
        """C4: remaining dischargeable capacity 3 (80%)."""
        self.assertEqual(self._parse(0xC4, b"\x50"), 80)

    def test_c6_rated_discharge_capacity(self):
        """C6: rated discharge capacity (6000 W)."""
        self.assertEqual(self._parse(0xC6, b"\x00\x00\x17\x70"), 6000)

    def test_c9_max_min_discharging_power(self):
        """C9: min/max discharging electric power (format: 'max/min')."""
        result = self._parse(
            0xC9,
            b"\x00\x00\x17\x70\x00\x00\x03\xe8",
        )
        self.assertEqual(result, "6000/1000")

    def test_cb_max_min_discharging_current(self):
        """CB: min/max discharging current (format: 'max/min')."""
        result = self._parse(0xCB, b"\x00\xc8\x00\x0a")
        self.assertEqual(result, "200/10")

    def test_d4_instantaneous_current(self):
        """D4: instantaneous charging/discharging current (signed)."""
        # Positive (charging): 150 (= 15.0 A)
        self.assertEqual(self._parse(0xD4, b"\x00\x00\x00\x96"), 150)
        # Negative (discharging): -100 (= -10.0 A)
        self.assertEqual(self._parse(0xD4, b"\xff\xff\xff\x9c"), -100)

    def test_d5_instantaneous_voltage(self):
        """D5: instantaneous voltage (signed)."""
        self.assertEqual(self._parse(0xD5, b"\x00\x00\x00\xc8"), 200)

    def test_db_system_interconnected_type(self):
        """DB: system-interconnected type."""
        self.assertEqual(
            self._parse(0xDB, b"\x00"), "reversePowerFlowAcceptable"
        )
        self.assertEqual(self._parse(0xDB, b"\x01"), "independent")
        self.assertEqual(
            self._parse(0xDB, b"\x02"), "reversePowerFlowNotAcceptable"
        )

    def test_d7_discharge_energy_reset(self):
        """D7: cumulative discharging energy reset setting."""
        self.assertEqual(self._parse(0xD7, b"\x00"), "Reset")

    def test_ec_discharging_power_setting(self):
        """EC: discharging electric energy setting (3000 W)."""
        self.assertEqual(self._parse(0xEC, b"\x00\x00\x0b\xb8"), 3000)

    def test_ee_discharging_current_setting(self):
        """EE: discharging current setting (160 = 16.0 A)."""
        self.assertEqual(self._parse(0xEE, b"\x00\xa0"), 160)

    def test_ef_rated_voltage_independent(self):
        """EF: rated voltage independent (200 V)."""
        self.assertEqual(self._parse(0xEF, b"\x00\xc8"), 200)


class TestEPCCoverage(unittest.TestCase):
    """Verify all EPCs defined in epc.py for 0x7E have parsers in EPC_FUNCTIONS."""

    def test_all_spec_epcs_have_parsers(self):
        spec_epcs = set(EPC_CODE[0x02][0x7E].keys())
        impl_epcs = set(ElectricVehicleCharger.EPC_FUNCTIONS.keys())
        missing = spec_epcs - impl_epcs
        self.assertEqual(
            missing,
            set(),
            f"EPCs defined in spec but missing from EPC_FUNCTIONS: "
            f"{', '.join(hex(e) for e in sorted(missing))}",
        )


class TestAsyncMethods(unittest.IsolatedAsyncioTestCase):
    """Test getMessage/setMessage via async convenience methods."""

    async def test_getOperationStatus_returns_bytes(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        status = await charger.getOperationStatus()
        self.assertEqual(status, b"\x30")

    async def test_setOperationStatus(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        result = await charger.setOperationStatus(0x31)
        self.assertTrue(result)

    async def test_getVehicleConnectionAndChargeableStatus_returns_bytes(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        status = await charger.getVehicleConnectionAndChargeableStatus()
        self.assertEqual(status, b"\x41")

    async def test_getMeasuredInstantaneousChargingElectricPower_returns_bytes(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        power = await charger.getMeasuredInstantaneousChargingElectricPower()
        self.assertEqual(power, b"\x00\x00\x05\xf8")

    async def test_getOperatingModeSetting_returns_bytes(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        mode = await charger.getOperatingModeSetting()
        self.assertEqual(mode, b"\x44")

    async def test_setOperatingModeSetting(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        result = await charger.setOperatingModeSetting(0x42)
        self.assertTrue(result)

    async def test_getVehicleID_returns_bytes(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        vehicle_id = await charger.getVehicleID()
        self.assertEqual(vehicle_id, b"\x00\x32")

    async def test_setChargingAmountSetting(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        result = await charger.setChargingAmountSetting(1000)
        self.assertTrue(result)

    async def test_setChargingCurrentSetting(self):
        api_connector = MockECHONETAPIClient()
        charger = ElectricVehicleCharger("192.168.1.50", api_connector)
        result = await charger.setChargingCurrentSetting(16)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
