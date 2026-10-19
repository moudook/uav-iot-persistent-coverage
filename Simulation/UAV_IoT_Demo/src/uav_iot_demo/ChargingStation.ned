package uav_iot_demo;

simple ChargingStation
{
    parameters:
        @class(ChargingStation);
        int stationId = 0;
        int maxConcurrentCharges = 2;
        double chargingPower = 50.0;
        int currentCharges = 0;

        @signal(chargingStarted);
        @signal(chargingCompleted);
        @signal(queueLength);
        @statistic(queueLength;record=count,vector);
    gates:
        inout chargingPort;
}
