#ifndef __UAV_IOT_DEMO_MLBRIDGE_H_
#define __UAV_IOT_DEMO_MLBRIDGE_H_

#include <omnetpp.h>
#include <string>
#include <vector>

using namespace omnetpp;

namespace uav_iot_demo {

struct UavState {
    int id;
    double battery;
    double posX;
    double posY;
    std::string status;
};

class MlBridge : public cSimpleModule
{
  private:
    std::string host;
    int port;
    double stateInterval;
    int sockFd;
    bool connected;

    cMessage *stateTimer = nullptr;

    simsignal_t stateSentSignal;
    simsignal_t actionReceivedSignal;

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
    virtual void finish() override;

    bool connectToPython();
    void disconnectFromPython();
    std::string collectState();
    void sendState(const std::string& json);
    std::string receiveAction();
    void applyAction(const std::string& json);

  public:
    virtual ~MlBridge();
};

} // namespace uav_iot_demo

#endif
