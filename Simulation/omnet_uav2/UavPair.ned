import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.AdhocHost;
import inet.physicallayer.wireless.ieee80211.packetlevel.Ieee80211ScalarRadioMedium;

//
// Two-node link probe.
//
// Design notes, because both choices were forced by measured failures:
//
// 1. Every degree of freedom is a NETWORK-LEVEL parameter, and every one is
//    prefixed "sim" so it cannot shadow the submodule parameter it feeds.
//    Submodule patterns such as "**.uav[*].mobility.traceFile" do not match
//    through the module vector and are silently ignored by OMNeT++, so an
//    earlier sweep replayed one default trace at fourteen "distances" and
//    reported a flat 0.995 PDR out to 4 km.  A parameter that refers to itself
//    ("mobility.traceFile = traceFile") is also an error, hence the prefix.
//
// 2. Geometry is a 3-D BonnMotion trace (t x y z tuples), so altitude is real
//    and the analysis script derives distances from the same numbers the
//    simulator reads.
//
// Traffic is uav[0] -> uav[1] and uav[1] -> uav[0]: one delivery counter per
// direction, no contention, nothing else on the channel.
//
network UavPair
{
    parameters:
        string simTrace = default("traces/pair.movements");
        double simTxPower @unit(W) = default(0.1W);
        double simSensitivity @unit(dBm) = default(-85dBm);
        double simSnir @unit(dB) = default(4dB);
        double simInterval @unit(s) = default(0.1s);
        double simBitrate @unit(bps) = default(6Mbps);
        double simSigma = default(6);  // dB, plain double: LogNormalShadowing.sigma has no unit
        double simNoise @unit(dBm) = default(-94dBm);
        @display("bgb=800,800");

    submodules:
        configurator: Ipv4NetworkConfigurator {
            parameters:
                config = xml("<config><interface hosts='**' address='10.0.0.x' netmask='255.255.255.0'/></config>");
                @display("p=50,50;is=s");
        }
        radioMedium: Ieee80211ScalarRadioMedium {
            parameters:
                // Free space plus log-normal shadowing: the deterministic model
                // gives a step-function PDR(d), which is not a channel anyone can
                // fit a delivery model to.  sigma = 0 reproduces the step and is
                // kept as the control.
                pathLoss.typename = "inet.physicallayer.wireless.common.pathloss.LogNormalShadowing";
                pathLoss.sigma = parent.simSigma;
                // Match the Python simulator's noise floor (-174 dBm/Hz + 7 dB NF
                // over 20 MHz = -94 dBm); INET's default is -110 dBm, 16 dB quieter,
                // which would inflate every SNIR and flatter the link.
                backgroundNoise.power = parent.simNoise;
                @display("p=50,150");
        }
        uav[2]: AdhocHost {
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
