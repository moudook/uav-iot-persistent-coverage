#include "ChargingStation.h"

namespace uav_iot_demo {

Define_Module(ChargingStation);

void ChargingStation::initialize()
{
    stationId = par("stationId").intValue();
    maxConcurrentCharges = par("maxConcurrentCharges").intValue();
    currentCharges = 0;
    chargingPower = par("chargingPower").doubleValue();

    chargingStartedSignal = registerSignal("chargingStarted");
    chargingCompletedSignal = registerSignal("chargingCompleted");
    queueLengthSignal = registerSignal("queueLength");

    EV_INFO << "ChargingStation [" << stationId << "] initialized - max concurrent: "
            << maxConcurrentCharges << endl;

    emit(queueLengthSignal, 0.0);
}

void ChargingStation::handleMessage(cMessage *msg)
{
    std::string msgName = msg->getName();

    if (msgName.find("chargingRequest") != std::string::npos) {
        if (currentCharges < maxConcurrentCharges) {
            currentCharges++;
            EV_INFO << "ChargingStation [" << stationId << "] accepted UAV - "
                    << currentCharges << "/" << maxConcurrentCharges << " slots used" << endl;

            emit(chargingStartedSignal, 1.0);
            emit(queueLengthSignal, (double)currentCharges);

            cMessage *response = new cMessage("chargingResponse_start");
            send(response, "chargingPort");
        } else {
            EV_WARN << "ChargingStation [" << stationId << "] queue full - rejecting request" << endl;
            emit(queueLengthSignal, (double)currentCharges);

            cMessage *response = new cMessage("chargingResponse_busy");
            send(response, "chargingPort");
        }
    }
    else if (msgName.find("chargingComplete") != std::string::npos) {
        if (currentCharges > 0) currentCharges--;

        EV_INFO << "ChargingStation [" << stationId << "] UAV complete - "
                << currentCharges << "/" << maxConcurrentCharges << " slots used" << endl;

        emit(chargingCompletedSignal, 1.0);
        emit(queueLengthSignal, (double)currentCharges);
    }

    delete msg;
}

void ChargingStation::finish()
{
    EV_INFO << "ChargingStation [" << stationId << "] final state - "
            << currentCharges << " active charges" << endl;
}

} // namespace uav_iot_demo
