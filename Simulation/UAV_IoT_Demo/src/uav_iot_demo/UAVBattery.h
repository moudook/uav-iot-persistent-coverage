#ifndef __UAV_IOT_DEMO_UAVBATTERY_H_
#define __UAV_IOT_DEMO_UAVBATTERY_H_

#include <omnetpp.h>

using namespace omnetpp;

namespace uav_iot_demo {

class UAVBattery : public cSimpleModule
{
  private:
    double currentEnergy;
    double energyCapacity;
    double dischargeRate;
    double idleDischargeRate;
    double chargeRate;
    double lowBatteryThreshold;
    double criticalBatteryThreshold;
    bool isCharging;
    std::string uavId;

    cMessage *dischargeTimer = nullptr;

    simsignal_t batteryLevelSignal;
    simsignal_t batteryStatusSignal;
    simsignal_t batteryDrainedSignal;
    simsignal_t batteryChargedSignal;

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
    virtual void finish() override;

    void startCharging();
    void stopCharging();
    void discharge();
    void updateBatteryLevel(double delta);
    double getBatteryPercentage() const;

  public:
    virtual ~UAVBattery();
};

} // namespace uav_iot_demo

#endif
