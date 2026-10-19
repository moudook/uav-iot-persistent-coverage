#ifndef __UAV_IOT_DEMO_CHARGINGSTATION_H_
#define __UAV_IOT_DEMO_CHARGINGSTATION_H_

#include <omnetpp.h>
#include <vector>

using namespace omnetpp;

namespace uav_iot_demo {

class ChargingStation : public cSimpleModule
{
  private:
    int stationId;
    int maxConcurrentCharges;
    int currentCharges;
    double chargingPower;

    simsignal_t chargingStartedSignal;
    simsignal_t chargingCompletedSignal;
    simsignal_t queueLengthSignal;

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
    virtual void finish() override;

  public:
    virtual ~ChargingStation() {}
};

} // namespace uav_iot_demo

#endif
