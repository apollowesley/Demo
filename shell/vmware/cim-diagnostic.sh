#!/bin/sh 

INTEROP_CLASSES="CIM_Namespace \
CIM_RegisteredProfile \
CIM_IndicationFilter \
CIM_ListenerDestination \
CIM_IndicationSubscription "

IMPL_CLASSES="CIM_Sensor \
OMC_RawIpmiSensor \
OMC_RawIpmiEntity \
CIM_ComputerSystem \
CIM_Chassis \
CIM_SoftwareIdentity \
CIM_Memory \
CIM_PhysicalMemory \
CIM_Processor \
CIM_LogRecord \
CIM_RecordLog \
CIM_EthernetPort \
CIM_PowerSupply \
CIM_PCIDevice \
VMware_StorageExtent \
VMware_Controller \
VMware_StorageVolume \
VMware_Battery \
VMware_SASSATAPort "

echo "[`date`] CIM Diagnostic dump for root/interop"
for CLASS in $INTEROP_CLASSES 
do
   echo "[`date`] Dumping instances of $CLASS"
   enum_instances $CLASS root/interop
done

echo "[`date`] CIM Diagnostic dump for root/cimv2"
for CLASS in $IMPL_CLASSES 
do
   echo "[`date`] Dumping instances of $CLASS"
   enum_instances $CLASS
done
echo "[`date`] CIM Diagnostic dump completed"
/bin/ticket --reap
