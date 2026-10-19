package uav_iot_demo;

simple UAVBattery
{
    parameters:
        @class(UAVBattery);
        double initialEnergy = 100;
        double energyCapacity = 100;
        double dischargeRate = 0.5;
        double idleDischargeRate = 0.1;
        double chargeRate = 2.0;
        double lowBatteryThreshold = 20.0;
        double criticalBatteryThreshold = 10.0;
        bool isCharging = false;
        string uavId = "";

        @signal(batteryLevel);
        @signal(batteryStatus);
        @signal(batteryDrained);
        @signal(batteryCharged);
        @statistic(batteryLevel;record=count,vector);
        @statistic(batteryStatus;record=count,vector);
    gates:
        inout charge;
}
