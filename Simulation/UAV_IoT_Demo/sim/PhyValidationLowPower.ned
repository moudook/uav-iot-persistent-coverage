//
// PhyValidationLowPower: the same scenario with the UAV's transmit power
// set to 1 pW (-120 dBm) DIRECTLY in the NED file.
//
// The point is to separate two hypotheses:
//   (a) the ini key does not reach the radio, so the "control" never
//       changed anything; or
//   (b) the radio chain does not gate reception at all.
//
// A NED assignment is applied before the ini, so if the link still closes
// with 1 pW written in the NED file, the ini is exonerated and the radio
// chain is the problem.
//
network PhyValidationLowPower
{
    parameters:
        int numSensors = default(4);
        @display("bgb=1000,500");

    submodules:
        radioMedium: Ieee80211ScalarRadioMedium {
            @display("p=50,50");
            backgroundNoise.power = -93.99dBm;
            pathLoss.typename = "BreakpointPathLoss";
            pathLoss.l01 = 40.04dB;
            pathLoss.l02 = 40.04dB;
            pathLoss.alpha1 = 2.0;
            pathLoss.alpha2 = 2.0;
            pathLoss.breakpointDistance = 1m;
        }

        uav: AdhocHost {
            @display("i=device/drone");
            // 1 pW = -120 dBm.  The receivers need -93.99 dBm, so with the
            // power actually applied the link CANNOT close at any range.
            wlan[0].radio.transmitter.power = 0.000000000001W;
            wlan[0].radio.transmitter.bitrate = 24Mbps;
            wlan[0].radio.centerFrequency = 2.437GHz;
            wlan[0].radio.bandwidth = 20MHz;
            wlan[0].radio.receiver.bandwidth = 20MHz;
            wlan[0].radio.receiver.sensitivity = -93.99dBm;
            wlan[0].radio.receiver.snirThreshold = 2dB;
            wlan[0].radio.receiver.snirThresholdMode = "mean";
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
