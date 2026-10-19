package sim;

import inet.node.inet.AdhocHost;
import inet.physicallayer.wireless.ieee80211.packetlevel.Ieee80211ScalarRadioMedium;
import inet.applications.udpapp.UdpSink;
import inet.applications.udpapp.UdpApp;
import inet.queueing.source.ActivePacketSource;
import inet.networklayer.udp.UdpSocketIo;

//
// PHY validation scenario.
//
// Purpose: independently verify the report's Table IV link budget and the
// Python reference PHY (ml_impl/uav_wireless/wireless.py) using INET's
// standards-faithful 802.11 radio stack.
//
// Geometry matches the report exactly:
//   * UAV base station at altitude z0 = 50 m,
//   * ground IoT sensors at horizontal range d = 10..80 m,
//   * 3-D slant range is therefore sqrt(d^2 + z0^2).
//
// Radio parameters are taken from Table IV:
//   * 0.5 W (27 dBm) transmit power, 2.437 GHz, 20 MHz,
//   * effective noise floor -93.99 dBm = k*T*B*NF (NF = 7 dB),
//   * link closure requires SNR >= 2.0 dB (the lowest MCS sensitivity
//     used by the Python MCS table).
//
// The path loss model is BreakpointPathLoss with breakpoint 1 m, which
// evaluates to  PL(d) = PL(1m) + 10*n*log10(d/1m)  -- algebraically
// identical to the Python log_distance_pl(), so the two can be compared
// numerically rather than only functionally.
//
network PhyValidation
{
    parameters:
        int numSensors = default(8);
        @display("bgb=1000,500");

    submodules:
        radioMedium: Ieee80211ScalarRadioMedium {
            @display("p=50,50");
            // Python noise floor: k*T*B*NF = 3.99e-13 W = -93.99 dBm
            backgroundNoise.power = -93.99dBm;
            // Log-distance path loss, algebraically identical to the Python
            // log_distance_pl(): PL(d) = PL(1m) + 10*n*log10(d/1m).
            pathLoss.typename = "BreakpointPathLoss";
            pathLoss.l01 = 40.04dB;   // PL at 1 m, 2.4 GHz free space
            pathLoss.l02 = 40.04dB;
            pathLoss.alpha1 = 2.0;    // free-space (LoS) exponent
            pathLoss.alpha2 = 2.0;
            pathLoss.breakpointDistance = 1m;
        }

        uav: AdhocHost {
            @display("i=device/drone");
            wlan[0].radio.transmitter.power = 0.5W;
            wlan[0].radio.transmitter.bitrate = 24Mbps;
            wlan[0].radio.centerFrequency = 2.437GHz;
            wlan[0].radio.bandwidth = 20MHz;
            wlan[0].radio.receiver.bandwidth = 20MHz;
            wlan[0].radio.receiver.sensitivity = -93.99dBm;
            wlan[0].radio.receiver.snirThreshold = 2dB;
            // snirThresholdMode must NOT be the default "min": that computes
            // SNR against min(noise, interference), which is zero when there
            // is no interferer, making the SNR check vacuous.
            wlan[0].radio.receiver.snirThresholdMode = "mean";
            // The 802.11 error model MUST be left enabled.  Disabling it
            // (errorModel.typename = "") removes the only component that
            // actually gates reception in Ieee80211Receiver, and the link
            // then "closes" at any range: a control run with the transmit
            // power crushed by 60 dB still delivered every frame.
            mobility.initialX = 0m;
            mobility.initialY = 0m;
            mobility.initialZ = 50m;
        }

        sensor[numSensors]: AdhocHost {
            @display("i=device/sensor");
            wlan[0].radio.transmitter.power = 0.5W;
            wlan[0].radio.transmitter.bitrate = 24Mbps;
            wlan[0].radio.centerFrequency = 2.437GHz;
            wlan[0].radio.bandwidth = 20MHz;
            wlan[0].radio.receiver.bandwidth = 20MHz;
            wlan[0].radio.receiver.sensitivity = -93.99dBm;
            wlan[0].radio.receiver.snirThreshold = 2dB;
            wlan[0].radio.receiver.snirThresholdMode = "mean";
            mobility.initialX = 0m;
            mobility.initialY = 0m;
            mobility.initialZ = 0m;
        }
}
