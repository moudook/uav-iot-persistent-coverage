import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.AdhocHost;
import inet.physicallayer.wireless.ieee80211.packetlevel.Ieee80211ScalarRadioMedium;

//
// Contention probe.
//
// All "sim"-prefixed network parameters, for the reasons documented in
// UavPair.ned: submodule patterns that pass through a module vector are
// silently ignored, and a parameter that refers to itself is an error.
//
// Every node transmits to uav[0], except uav[0] which transmits to uav[1].
// So uav[0] is both a contender and the measurement point: its
// "packets received" divided by the sum of everybody's "packets sent" is the
// aggregate delivery ratio under MAC contention at a known node density.
//
// Geometry comes from a 3-D BonnMotion trace supplied by the caller.
//
network UavSwarm
{
    parameters:
        int simNumUavs = default(8);
        string simTrace = default("traces/swarm.movements");
        double simTxPower @unit(W) = default(0.1W);
        double simSensitivity @unit(dBm) = default(-85dBm);
        double simSnir @unit(dB) = default(4dB);
        double simInterval @unit(s) = default(0.1s);
        double simBitrate @unit(bps) = default(6Mbps);
        @display("bgb=1000,1000");

    submodules:
        configurator: Ipv4NetworkConfigurator {
            parameters:
                config = xml("<config><interface hosts='**' address='10.0.0.x' netmask='255.255.255.0'/></config>");
                @display("p=50,50;is=s");
        }
        radioMedium: Ieee80211ScalarRadioMedium {
            parameters:
                @display("p=50,150");
        }
        uav[simNumUavs]: AdhocHost {
            parameters:
                @display("r=,,#0080ff");
                mobility.typename = "BonnMotionMobility";
                mobility.traceFile = parent.simTrace;
                mobility.is3D = true;
                mobility.nodeId = index;

                numApps = 1;
                app[0].typename = "UdpBasicApp";
                app[0].destAddresses = index == 0 ? "uav[1]" : "uav[0]";
                app[0].destPort = 1000;
                app[0].messageLength = 64B;
                app[0].sendInterval = parent.simInterval;
                app[0].startTime = uniform(0s, parent.simInterval);
                app[0].localPort = 1000;

                wlan[0].bitrate = parent.simBitrate;
                wlan[0].mac.dcf.channelAccess.cwMin = 7;
                wlan[0].radio.transmitter.power = parent.simTxPower;
                wlan[0].radio.receiver.sensitivity = parent.simSensitivity;
                wlan[0].radio.receiver.snirThreshold = parent.simSnir;
        }
}
