# Makefile for UAV_IoT_Demo (OMNeT++ 6.x)
# Run 'make' in this directory to build the project

# OMNeT++ / opp_env paths (set via environment or edit here)
OMNETPP_ROOT ?= $(shell omnetpp -v 2>/dev/null | grep -oP 'OMNETPP_ROOT=\K.*' || echo "/opt/omnetpp-6.0.3")
INET_ROOT ?= $(shell find /opt -maxdepth 2 -name "inet" -type d 2>/dev/null | head -1 || echo "../inet4.6")
SIMU5G_ROOT ?= $(shell find /opt -maxdepth 2 -name "simu5g" -type d 2>/dev/null | head -1 || echo "../simu5g-1.4.3")

# Source directories
MSGCLEAN = .
SRC_DIR = src/uav_iot_demo
BUILD_DIR = out

# Source files
CC = g++
CFLAGS = -std=c++17 -O2 -Wall
OMNETPP_INCL = -I$(OMNETPP_ROOT)/include -I$(OMNETPP_ROOT)/include/omnetpp
INET_INCL = -I$(INET_ROOT)/src
SIMU5G_INCL = -I$(SIMU5G_ROOT)/src
PKG_INCL = -I$(SRC_DIR)

SRCS = $(SRC_DIR)/UAVBattery.cc $(SRC_DIR)/ChargingStation.cc
OBJS = $(patsubst %.cc,$(BUILD_DIR)/%.o,$(SRCS))

# Target
TARGET = uav_iot_demo

.PHONY: all clean

all: $(BUILD_DIR) $(TARGET)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)/$(SRC_DIR)

$(BUILD_DIR)/%.o: %.cc
	$(CC) $(CFLAGS) $(OMNETPP_INCL) $(INET_INCL) $(SIMU5G_INCL) $(PKG_INCL) -c $< -o $@

$(TARGET): $(OBJS)
	@echo "Linking $(TARGET)..."
	$(CC) $(OBJS) -L$(OMNETPP_ROOT)/lib -lomnetpp -o $(BUILD_DIR)/$(TARGET)
	@echo "Build complete. Binary: $(BUILD_DIR)/$(TARGET)"

clean:
	rm -rf $(BUILD_DIR)
	@echo "Clean complete."
