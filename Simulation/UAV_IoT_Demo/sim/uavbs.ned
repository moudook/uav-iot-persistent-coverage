package sim;

import inet.wireless.wirelessLink.WirelessLink;
import inet.wireless.wirelessMedium.RadioMedium;
import inet.wireless.ieee80211.Ieee80211ScalarRadioMedium;
import inet.node.inet.StandardHost;
import inet.node.inet.Router;

// A UAV flying as an aerial base station for IoT sensors.
// Position is commanded by the MAPPO actor over the TCP bridge
// (see python_bridge/omnetpp_bridge.py); this module owns the 802.11 PHY.
module UavBaseStation extends StandardHost
{
    parameters:
        @display("bgb=200,200");
        // IEEE 802.11g, channel 6 (2.437 GHz) -- matches wireless.py's f_hz
        string radioType = "Ieee80211ScalarRadioMedium";
        string channel = "channel6";
        string opMode = "g";
        bitrate = default(24Mbps);
        txPower = default(0.5W);          // P_tx in Table VI
        sensitivity = default(-91dBm);
        centerFrequency = default(2.437GHz);
        bandWidth = default(20MHz);
        string mobilityModel = "LinearMobility";
        double speed = default(5mps);     // v_max in Table VI
        double batteryCapacity = default(30000);  // J
        double batteryLevel = default(1.0);
        bool reserveAvailable = default(false);

    gates:
        input upperLayerIn;
        output upperLayerOut;

    submodules:
        radio: radioType {
            parameters:
                transmitter.0.centerFrequency = centerFrequency;
                transmitter.0.bandwidth = bandWidth;
                transmitter.0.txPower = txPower;
                transmitter.0.sensitivity = sensitivity;
                receiver.0.centerFrequency = centerFrequency;
                receiver.0.bandwidth = bandWidth;
                transmitter.0.bitrate = bitrate;
                receiver.0.bitrate = bitrate;
                @display("p=60,60");
        }
        antenna0: ^WirelessAntenna {
            parameters:
                @display("p=60,110");
        }

    connections:
        upperLayerIn <--> radio <--> antenna0;
}