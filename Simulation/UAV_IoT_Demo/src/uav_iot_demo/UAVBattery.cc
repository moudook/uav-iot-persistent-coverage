#include "UAVBattery.h"

namespace uav_iot_demo {

Define_Module(UAVBattery);

UAVBattery::~UAVBattery()
{
    cancelAndDelete(dischargeTimer);
}

void UAVBattery::initialize()
{
    currentEnergy = par("initialEnergy").doubleValue();
    energyCapacity = par("energyCapacity").doubleValue();
    dischargeRate = par("dischargeRate").doubleValue();
    idleDischargeRate = par("idleDischargeRate").doubleValue();
    chargeRate = par("chargeRate").doubleValue();
    lowBatteryThreshold = par("lowBatteryThreshold").doubleValue();
    criticalBatteryThreshold = par("criticalBatteryThreshold").doubleValue();
    isCharging = par("isCharging").boolValue();
    uavId = par("uavId").stdstringValue();

    batteryLevelSignal = registerSignal("batteryLevel");
    batteryStatusSignal = registerSignal("batteryStatus");
    batteryDrainedSignal = registerSignal("batteryDrained");
    batteryChargedSignal = registerSignal("batteryCharged");

    EV_INFO << "UAVBattery [" << uavId << "] initialized with " << currentEnergy << " J" << endl;

    emit(batteryLevelSignal, getBatteryPercentage());
    emit(batteryStatusSignal, isCharging ? 1.0 : 0.0);

    if (!isCharging) {
        dischargeTimer = new cMessage("dischargeTimer");
        scheduleAt(simTime() + 1.0, dischargeTimer);
    }
}

void UAVBattery::handleMessage(cMessage *msg)
{
    if (msg == dischargeTimer) {
        if (!isCharging) {
            discharge();
            scheduleAt(simTime() + 1.0, dischargeTimer);
        }
    }
    else if (msg->isSelfMessage()) {
        // Handle charging completion
        if (isCharging) {
            startCharging();
        }
    }
    else {
        // Message from gate - check if it is a charge command
        std::string msgName = msg->getName();
        if (msgName.find("charge") != std::string::npos) {
            if (msgName.find("start") != std::string::npos) {
                startCharging();
            } else if (msgName.find("stop") != std::string::npos) {
                stopCharging();
            }
        }
        delete msg;
    }
}

void UAVBattery::discharge()
{
    if (currentEnergy > 0) {
        currentEnergy -= dischargeRate;
        if (currentEnergy < 0) currentEnergy = 0;

        EV_INFO << "UAVBattery [" << uavId << "] discharging: " << currentEnergy << " J ("
                << getBatteryPercentage() << "%)" << endl;

        emit(batteryLevelSignal, getBatteryPercentage());

        if (getBatteryPercentage() <= criticalBatteryThreshold) {
            EV_WARN << "UAVBattery [" << uavId << "] CRITICAL battery level!" << endl;
            emit(batteryStatusSignal, -1.0); // Critical
            emit(batteryDrainedSignal, 1.0);
        } else if (getBatteryPercentage() <= lowBatteryThreshold) {
            EV_WARN << "UAVBattery [" << uavId << "] LOW battery level - return to base!" << endl;
            emit(batteryStatusSignal, -2.0); // Low - return to base
        } else {
            emit(batteryStatusSignal, 0.0); // Normal discharge
        }
    }
}

void UAVBattery::startCharging()
{
    isCharging = true;
    if (dischargeTimer && dischargeTimer->isScheduled()) {
        cancelEvent(dischargeTimer);
    }

    double energyNeeded = energyCapacity - currentEnergy;
    double chargeTime = energyNeeded / chargeRate;

    EV_INFO << "UAVBattery [" << uavId << "] charging - " << chargeTime << "s to full" << endl;
    emit(batteryStatusSignal, 1.0); // Charging

    currentEnergy += chargeRate;
    if (currentEnergy > energyCapacity) currentEnergy = energyCapacity;

    emit(batteryLevelSignal, getBatteryPercentage());
    emit(batteryChargedSignal, currentEnergy);

    if (currentEnergy >= energyCapacity) {
        stopCharging();
    }
}

void UAVBattery::stopCharging()
{
    isCharging = false;
    EV_INFO << "UAVBattery [" << uavId << "] charging stopped - " << currentEnergy << " J" << endl;

    emit(batteryStatusSignal, 0.0);
    emit(batteryLevelSignal, getBatteryPercentage());

    if (!dischargeTimer) {
        dischargeTimer = new cMessage("dischargeTimer");
    }
    scheduleAt(simTime() + 1.0, dischargeTimer);
}

double UAVBattery::getBatteryPercentage() const
{
    return (currentEnergy / energyCapacity) * 100.0;
}

void UAVBattery::updateBatteryLevel(double delta)
{
    currentEnergy += delta;
    if (currentEnergy > energyCapacity) currentEnergy = energyCapacity;
    if (currentEnergy < 0) currentEnergy = 0;
    emit(batteryLevelSignal, getBatteryPercentage());
}

void UAVBattery::finish()
{
    EV_INFO << "UAVBattery [" << uavId << "] final energy: " << currentEnergy << " J ("
            << getBatteryPercentage() << "%)" << endl;
}

} // namespace uav_iot_demo
