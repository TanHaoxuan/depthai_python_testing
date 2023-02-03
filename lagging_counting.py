#!/usr/bin/env python3

import cv2
import depthai as dai



# Create pipeline
pipeline = dai.Pipeline()



# Define 

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
monoB.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
manipB.setMaxOutputFrameSize(monoB.getResolutionHeight()*monoB.getResolutionWidth()*3)
monoB.setFps(30)

monoC.setBoardSocket(dai.CameraBoardSocket.CAM_C) 
monoC.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
manipC.setMaxOutputFrameSize(monoC.getResolutionHeight()*monoC.getResolutionWidth()*3)
monoC.setFps(30)

monoD.setBoardSocket(dai.CameraBoardSocket.CAM_D) 
monoD.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
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


    sensIso=200

    expTime_state1 = 1000
    expTime_state2 = 10000
    expTime = 1000

    frame_lagging_A = 0
    frame_lagging_B = 0
    frame_lagging_C = 0
    frame_lagging_D = 0


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
        # inA = qA.get()
        inB = qB.get()
        inC = qC.get()
        inD = qD.get()

        
        # exposure_received_A=int(inA.getExposureTime().total_seconds()*1000000)
        exposure_received_B=int(inB.getExposureTime().total_seconds()*1000000)
        exposure_received_C=int(inC.getExposureTime().total_seconds()*1000000)
        exposure_received_D=int(inD.getExposureTime().total_seconds()*1000000)

        #received exposure == sent exposure
        # if(exposure_received_A == exposure_sent_A):   

        #     print(f"frame lagging A = {frame_lagging_A}")
        #     #reset
        #     frame_lagging_A=0
        # else:   #not receiving the sent exposure
        #     frame_lagging_A+=1
        if(exposure_received_B == exposure_sent_B):   

            print(f"frame lagging B = {frame_lagging_B}")
            #reset
        else:   #not receiving the sent exposure
            frame_lagging_B+=1

        if(exposure_received_C == exposure_sent_C):   

            print(f"frame lagging C = {frame_lagging_C}")
            #reset
        else:   #not receiving the sent exposure
            frame_lagging_C+=1

        if(exposure_received_D == exposure_sent_D):   

            print(f"frame lagging D = {frame_lagging_D}")
            #reset
        else:   #not receiving the sent exposure
            frame_lagging_D+=1

        #display image
        cv2.imshow("camb", inB.getCvFrame())
        key = cv2.waitKey(1)


        if(expTime==expTime_state1 and (exposure_received_B==exposure_sent_B) and (exposure_received_C==exposure_sent_C) and (exposure_received_D==exposure_sent_D)): #at stage 1 and received the sent exposure
            
            #send command to change to another state
            expTime=expTime_state2
            exposure_sent_A=expTime
            exposure_sent_B=expTime
            exposure_sent_C=expTime
            exposure_sent_D=expTime

            frame_lagging_A=0
            frame_lagging_B=0
            frame_lagging_C=0
            frame_lagging_D=0


            ctrl = dai.CameraControl()
            ctrl.setManualExposure(expTime, sensIso)
            print("Setting manual exposure, time:", expTime, "iso:", sensIso)
            controlQueue.send(ctrl)

        
        elif(expTime==expTime_state2 and (exposure_received_B==exposure_sent_B) and (exposure_received_C==exposure_sent_C) and (exposure_received_D==exposure_sent_D)): #at stage 2 and received the sent exposure

            #send command to change to another state
            expTime=expTime_state1
            exposure_sent_A=expTime
            exposure_sent_B=expTime
            exposure_sent_C=expTime
            exposure_sent_D=expTime

            frame_lagging_A=0
            frame_lagging_B=0
            frame_lagging_C=0
            frame_lagging_D=0
            
            ctrl = dai.CameraControl()
            ctrl.setManualExposure(expTime, sensIso)
            print("Setting manual exposure, time:", expTime, "iso:", sensIso)
            controlQueue.send(ctrl)


