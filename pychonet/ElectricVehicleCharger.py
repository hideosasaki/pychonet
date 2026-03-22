# pychonet/ElectricVehicleCharger.py
from pychonet.EchonetInstance import EchonetInstance
from pychonet.lib.epc_functions import (
    _int,
    _signed_int,
    _unsigned_long,
    _unsigned_short,
    _signed_long,
    DICT_30_ON_OFF,
)


def _max_min_int(edt):
    """Parse minimum/maximum values from 8-byte EPC data."""
    max_val = str(int.from_bytes(edt[0:4], "big"))
    min_val = str(int.from_bytes(edt[4:8], "big"))
    return f"{max_val}/{min_val}"


def _max_min_short_int(edt):
    """Parse minimum/maximum values from 4-byte EPC data."""
    max_val = str(int.from_bytes(edt[0:2], "big"))
    min_val = str(int.from_bytes(edt[2:4], "big"))
    return f"{max_val}/{min_val}"


class ElectricVehicleCharger(EchonetInstance):
    EPC_FUNCTIONS = {
        # Electric vehicle charger/discharger class (0x027E)
        0x80: [_int, DICT_30_ON_OFF],  # Operation status
        0xC0: _unsigned_long,  # Dischargeable capacity of vehicle mounted battery 1
        0xC1: _unsigned_long,  # Dischargeable capacity of vehicle mounted battery 2
        0xC2: _unsigned_long,  # Remaining dischargeable capacity of vehicle mounted battery 1
        0xC3: _unsigned_long,  # Remaining dischargeable capacity of vehicle mounted battery 2
        0xC4: _int,  # Remaining dischargeable capacity of vehicle mounted battery 3
        0xC5: _unsigned_long,  # Rated charge capacity
        0xC6: _unsigned_long,  # Rated discharge capacity
        0xC7: [_int, {0x30: "Vehicle not connected", 0x40: "Connected to vehicle, Not chargeable", 0x41: "Connected to vehicle, Chargeable", 0x42: "Connected to vehicle, Dischargeable", 0x43: "Connected to vehicle, Chargeable and Dischargeable", 0x44: "Connected to vehicle, chargeable status unknown", 0xFF: "Undetermined"}],  # Vehicle connection and chargeable/dischargeable status
        0xC8: _max_min_int,  # Minimum/maximum charging electric energy
        0xC9: _max_min_int,  # Minimum/maximum discharging electric energy
        0xCA: _max_min_short_int,  # Minimum/maximum charging current
        0xCB: _max_min_short_int,  # Minimum/maximum discharging current
        0xD0: _unsigned_long,  # Used capacity of vehicle-mounted battery 1
        0xD1: _unsigned_long,  # Used capacity of vehicle-mounted battery 2
        0xD2: _unsigned_short,  # Rated voltage
        0xD3: _signed_long,  # Measured instantaneous charging/discharging electric energy
        0xD4: _signed_int,  # Measured instantaneous charging/discharging current
        0xD5: _signed_int,  # Measured instantaneous charging/discharging voltage
        0xD6: _unsigned_long,  # Measured cumulative amount of discharging electric energy
        0xD7: [_int, {0x00: "Reset"}],  # Cumulative amount of discharging electric energy reset setting
        0xD8: _unsigned_long,  # Measured cumulative amount of charging electric energy
        0xD9: [_int, {0x00: "Reset"}],  # Cumulative amount of charging electric energy reset setting
        0xDA: [_int, {0x40: "Other", 0x42: "Charging", 0x43: "Discharging", 0x44: "Standby", 0x47: "Idle"}],  # Operating mode setting
        0xDB: [_int, {0x00: "reversePowerFlowAcceptable", 0x01: "independent", 0x02: "reversePowerFlowNotAcceptable"}],  # System-interconnected type
        0xE2: _unsigned_long,  # Remaining stored electricity of vehicle-mounted battery 1
        0xE3: _unsigned_long,  # Remaining stored electricity of vehicle-mounted battery 2
        0xE4: _int,  # Remaining stored electricity of vehicle-mounted battery 3
        0xE6: _int,  # Vehicle ID
        0xE7: _unsigned_long,  # Charging amount setting 1
        0xE9: _unsigned_long,  # Charging amount setting 2
        0xEB: _unsigned_long,  # Charging electric energy setting
        0xEC: _unsigned_long,  # Discharging electric energy setting
        0xED: _unsigned_short,  # Charging current setting
        0xEE: _unsigned_short,  # Discharging current setting
        0xEF: _unsigned_short,  # Rated voltage (Independent)
    }

    def __init__(self, host, api_connector=None, instance=0x1):
        self._eojgc = 0x02
        self._eojcc = 0x7E
        EchonetInstance.__init__(
            self, host, self._eojgc, self._eojcc, instance, api_connector
        )

    # --- Operation status (0x80) ---

    async def getOperationStatus(self):
        return await self.getMessage(0x80)

    async def setOperationStatus(self, status):
        return await self.setMessage(0x80, status)

    # --- Charge capacity and status ---

    async def getRatedChargeCapacity(self):
        return await self.getMessage(0xC5)

    async def getRatedDischargeCapacity(self):
        return await self.getMessage(0xC6)

    async def getVehicleConnectionAndChargeableStatus(self):
        return await self.getMessage(0xC7)

    async def getMinimumMaximumChargingElectricPower(self):
        return await self.getMessage(0xC8)

    async def getMinimumMaximumDischargingElectricPower(self):
        return await self.getMessage(0xC9)

    async def getMinimumMaximumChargingCurrent(self):
        return await self.getMessage(0xCA)

    async def getMinimumMaximumDischargingCurrent(self):
        return await self.getMessage(0xCB)

    # --- Dischargeable capacity ---

    async def getDischargeableCapacity1(self):
        return await self.getMessage(0xC0)

    async def getDischargeableCapacity2(self):
        return await self.getMessage(0xC1)

    async def getRemainingDischargeableCapacity1(self):
        return await self.getMessage(0xC2)

    async def getRemainingDischargeableCapacity2(self):
        return await self.getMessage(0xC3)

    async def getRemainingDischargeableCapacity3(self):
        return await self.getMessage(0xC4)

    # --- Charger type and connection ---

    async def getChargerType(self):
        return await self.getMessage(0xCC)

    async def getVehicleConnectionConfirmation(self):
        return await self.getMessage(0xCD)

    async def getChargeableCapacityOfVehicleMountedBattery(self):
        return await self.getMessage(0xCE)

    async def getRemainingChargeableCapacityOfVehicleMountedBattery(self):
        return await self.getMessage(0xCF)

    # --- Used capacity ---

    async def getUsedCapacityOfVehicleMountedBattery1(self):
        return await self.getMessage(0xD0)

    async def getUsedCapacityOfVehicleMountedBattery2(self):
        return await self.getMessage(0xD1)

    # --- Voltage ---

    async def getRatedVoltage(self):
        return await self.getMessage(0xD2)

    async def getRatedVoltageIndependent(self):
        return await self.getMessage(0xEF)

    # --- Instantaneous measurements ---

    async def getMeasuredInstantaneousChargingElectricPower(self):
        return await self.getMessage(0xD3)

    async def getMeasuredInstantaneousChargingDischargingCurrent(self):
        return await self.getMessage(0xD4)

    async def getMeasuredInstantaneousChargingDischargingVoltage(self):
        return await self.getMessage(0xD5)

    # --- Cumulative energy ---

    async def getMeasuredCumulativeAmountOfDischargingElectricEnergy(self):
        return await self.getMessage(0xD6)

    async def resetCumulativeAmountOfDischargingElectricEnergy(self):
        return await self.setMessage(0xD7, 0x00)

    async def getMeasuredCumulativeAmountOfChargingElectricEnergy(self):
        return await self.getMessage(0xD8)

    async def setCumulativeAmountOfChargingElectricEnergy(self):
        return await self.setMessage(0xD9, 0x00)

    # --- Operation mode (0xDA) ---

    async def getOperatingModeSetting(self):
        return await self.getMessage(0xDA)

    async def setOperatingModeSetting(self, mode):
        return await self.setMessage(0xDA, mode)

    # --- System-interconnected type (0xDB) ---

    async def getSystemInterconnectedType(self):
        return await self.getMessage(0xDB)

    # --- Remaining stored electricity ---

    async def getRemainingStoredElectricityOfVehicleMountedBattery1(self):
        return await self.getMessage(0xE2)

    async def getRemainingStoredElectricityOfVehicleMountedBattery2(self):
        return await self.getMessage(0xE3)

    async def getRemainingStoredElectricityOfVehicleMountedBattery3(self):
        return await self.getMessage(0xE4)

    # --- Vehicle ID ---

    async def getVehicleID(self):
        return await self.getMessage(0xE6)

    # --- Charging/Discharging settings ---

    async def getChargingAmountSetting1(self):
        return await self.getMessage(0xE7)

    async def setChargingAmountSetting(self, amount):
        return await self.setMessage(0xE7, amount)

    async def getChargingAmountSetting2(self):
        return await self.getMessage(0xE9)

    async def setChargingAmountSetting2(self, amount):
        return await self.setMessage(0xE9, amount)

    async def getChargingElectricPowerSetting(self):
        return await self.getMessage(0xEB)

    async def setChargingElectricPowerSetting(self, power):
        return await self.setMessage(0xEB, power)

    async def getDischargingElectricPowerSetting(self):
        return await self.getMessage(0xEC)

    async def setDischargingElectricPowerSetting(self, power):
        return await self.setMessage(0xEC, power)

    async def getChargingCurrentSetting(self):
        return await self.getMessage(0xED)

    async def setChargingCurrentSetting(self, current):
        return await self.setMessage(0xED, current)

    async def getDischargingCurrentSetting(self):
        return await self.getMessage(0xEE)

    async def setDischargingCurrentSetting(self, current):
        return await self.setMessage(0xEE, current)
