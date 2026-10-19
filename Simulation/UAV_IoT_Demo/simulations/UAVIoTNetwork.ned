package sim;

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.ethernet.Eth10G;
import inet.node.ethernet.Eth100M;
import inet.node.ethernet.Eth10M;
import inet.node.inet.Router;
import inet.node.inet.StandardHost;
import simu5g.common.binder.Binder;
import simu5g.common.carrierAggregation.CarrierAggregation;
import simu5g.nodes.NrUe;
import simu5g.nodes.gNodeB;
import simu5g.nodes.Upf;
import simu5g.world.radio.LteChannelControl;

network UAVIoTNetwork
{
    parameters:
        int numUe = default(3);
        int numIoTNodes = default(5);
        @display("bgb=1100,700");

    submodules:
        channelControl: LteChannelControl {
            @display("p=50,25;is=s");
        }
        configurator: Ipv4NetworkConfigurator {
            @display("p=50,125");
        }
        binder: Binder {
            @display("p=50,175;is=s");
        }
        carrierAggregation: CarrierAggregation {
            @display("p=50,225;is=s");
        }
        server: StandardHost {
            @display("p=200,125;i=device/server");
        }
        router: Router {
            @display("p=350,125;i=device/smallrouter");
        }
        upf: Upf {
            @display("p=500,125");
        }
        gnb: gNodeB {
            @display("p=650,200;is=vl");
        }
        ue[numUe]: NrUe {
            @display("p=650,350");
        }
        iotNode[numIoTNodes]: StandardHost {
            @display("p=200,350");
        }

    connections:
        server.pppg++ <--> Eth10G <--> router.pppg++;
        router.pppg++ <--> Eth10G <--> upf.filterGate;
        upf.pppg++ <--> Eth10G <--> gnb.ppp;
        for i = 0..numIoTNodes-1 {
            iotNode[i].pppg++ <--> Eth10M <--> router.pppg++;
        }
}
