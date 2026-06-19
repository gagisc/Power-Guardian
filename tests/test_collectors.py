import sys; sys.path.insert(0,"src")
from collectors.snmp_collector import SNMPCollector
from collectors.modbus_collector import ModbusCollector

def test_snmp_sim():
    c = SNMPCollector(oid_map={"inlet_power_w":"1.3.6.1.0.0"}, simulate=True)
    r = c.poll(); assert "inlet_power_w" in r

def test_modbus_sim():
    c = ModbusCollector(simulate=True)
    r = c.poll(); assert "output_power_kw" in r
