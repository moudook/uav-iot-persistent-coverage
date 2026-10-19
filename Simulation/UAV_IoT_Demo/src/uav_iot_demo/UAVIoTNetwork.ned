package uav_iot_demo;

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.Router;
import inet.node.inet.StandardHost;
import simu5g.common.binder.Binder;
import simu5g.common.carrierAggregation.CarrierAggregation;
import simu5g.nodes.gNodeB;
import simu5g.nodes.NrUe;
import simu5g.nodes.Upf;
import simu5g.world.radio.LteChannelControl;

network UAVIoTNetwork
{
    parameters:
        int numUAVs = 3;
        int numIoTNodes = 5;
        @display("bgb=1000,700");

    submodules:
        channelControl: LteChannelControl {
            @display("p=50,50;is=s");
        }
        configurator: Ipv4NetworkConfigurator {
            @display("p=50,100");
        }
        binder: Binder {
            @display("p=50,150;is=s");
        }
        carrierAggregation: CarrierAggregation {
            @display("p=50,200;is=s");
        }
        server: StandardHost {
            @display("p=200,100;i=device/server");
        }
        router: Router {
            @display("p=350,100;i=device/smallrouter");
        }
        upf: Upf {
            @display("p=500,100");
        }
        gnb: gNodeB {
            @display("p=650,200;is=vl");
        }
        ue[numUAVs]: NrUe {
            @display("p=650,350");
        }
        iotNode[numIoTNodes]: StandardHost {
            @display("p=200,350;i=app/sensor");
        }

    connections:
        server.pppg++ <--> Eth10G <--> router.pppg++;
        router.pppg++ <--> Eth10G <--> upf.filterGate;
        upf.pppg++ <--> Eth10G <--> gnb.ppp;
        for i = 0..numIoTNodes-1 {
            iotNode[i].pppg++ <--> Eth10G <--> router.pppg++;
        }
}
