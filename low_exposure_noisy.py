#!/usr/bin/env python3

import cv2
import depthai as dai

# Create pipeline
pipeline = dai.Pipeline()

#camera node
# monoA= pipeline.create(dai.node.MonoCamera)
monoB= pipeline.create(dai.node.MonoCamera)
monoC= pipeline.create(dai.node.MonoCamera)
monoD= pipeline.create(dai.node.MonoCamera)

#manip node : Capability to crop, resize, warp, … incoming image frames
# manipA = pipeline.create(dai.node.ImageManip)
manipB = pipeline.create(dai.node.ImageManip)
manipC = pipeline.create(dai.node.ImageManip)
manipD = pipeline.create(dai.node.ImageManip)

#manip out node : XLinkOut node. Sends messages over XLink.
# manipOutA = pipeline.create(dai.node.XLinkOut)
manipOutB = pipeline.create(dai.node.XLinkOut)
manipOutC = pipeline.create(dai.node.XLinkOut)
manipOutD = pipeline.create(dai.node.XLinkOut)

#controlXlinkin
controlIn = pipeline.create(dai.node.XLinkIn)

controlIn.setStreamName('control')
# manipOutA.setStreamName("A")
manipOutB.setStreamName("B")
manipOutC.setStreamName("C")
manipOutD.setStreamName("D")


# Properties

# monoA.setBoardSocket(dai.CameraBoardSocket.CAM_A) 
# monoA.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
# manipA.setMaxOutputFrameSize(monoA.getResolutionHeight()*monoA.getResolutionWidth()*3)
# monoA.setFps(30)

monoB.setBoardSocket(dai.CameraBoardSocket.CAM_B) 
monoB.setResolution(dai.MonoCameraProperties.SensorResolution.THE_1200_P)
manipB.setMaxOutputFrameSize(monoB.getResolutionHeight()*monoB.getResolutionWidth()*3)
monoB.setFps(30)

monoC.setBoardSocket(dai.CameraBoardSocket.CAM_C) 
monoC.setResolution(dai.MonoCameraProperties.SensorResolution.THE_1200_P)
manipC.setMaxOutputFrameSize(monoC.getResolutionHeight()*monoC.getResolutionWidth()*3)
monoC.setFps(30)

monoD.setBoardSocket(dai.CameraBoardSocket.CAM_A) 
monoD.setResolution(dai.MonoCameraProperties.SensorResolution.THE_1200_P)
manipD.setMaxOutputFrameSize(monoD.getResolutionHeight()*monoD.getResolutionWidth()*3)
monoD.setFps(30)


#Linking

# controlIn.out.link(monoA.inputControl)
# monoA.out.link(manipA.inputImage) 
# manipA.out.link(manipOutA.input)

controlIn.out.link(monoB.inputControl)
monoB.out.link(manipB.inputImage) 
manipB.out.link(manipOutB.input)

controlIn.out.link(monoC.inputControl)
monoC.out.link(manipC.inputImage) 
manipC.out.link(manipOutC.input)

controlIn.out.link(monoD.inputControl)
monoD.out.link(manipD.inputImage) 
manipD.out.link(manipOutD.input)


with dai.Device(pipeline) as device:
    # qA = device.getOutputQueue(manipOutA.getStreamName(), maxSize=4, blocking=False)
    qB = device.getOutputQueue(manipOutB.getStreamName(), maxSize=4, blocking=False)
    qC = device.getOutputQueue(manipOutC.getStreamName(), maxSize=4, blocking=False)
    qD = device.getOutputQueue(manipOutD.getStreamName(), maxSize=4, blocking=False)

    controlQueue = device.getInputQueue(controlIn.getStreamName())


    #ensure exposure_sent == exposure_received
    # inA = qA.get()
    inB = qB.get()
    inC = qC.get()
    inD = qD.get()

    # exposure_received_A=int(inA.getExposureTime().total_seconds()*1000000)
    # exposure_sent_A=exposure_received_A
    
    exposure_received_B=int(inB.getExposureTime().total_seconds()*1000000)
    exposure_sent_B=exposure_received_B
    
    exposure_received_C=int(inC.getExposureTime().total_seconds()*1000000)
    exposure_sent_C=exposure_received_C
    
    exposure_received_D=int(inD.getExposureTime().total_seconds()*1000000)
    exposure_sent_D=exposure_received_D

    while True:
        sensIso =100
        expTime = 20

        # inA = qA.get()
        inB = qB.get()
        inC = qC.get()
        inD = qD.get()
        
        #display image
        cv2.imshow("camb", inB.getCvFrame())
        key = cv2.waitKey(1)


        ctrl = dai.CameraControl()
        ctrl.setManualExposure(expTime, sensIso)
        # print("Setting manual exposure, time:", expTime, "iso:", sensIso)
        controlQueue.send(ctrl)



