package uav_iot_demo;

import inet.node.inet.StandardHost;

compound UAVModule
{
    parameters:
        string uavId = "";
        @display("i=app/mobile2");
    gates:
        inout ethg;
    submodules:
        host: StandardHost {
            @display("p=50,50");
        }
        battery: UAVBattery {
            parameters:
                uavId = this.uavId;
                @display("p=50,120");
        }
    connections:
        ethg <--> host.ethg;
}
