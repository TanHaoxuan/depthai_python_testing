#!/usr/bin/env python3
import cv2
import depthai as dai
import threading

# Create pipeline
pipeline = dai.Pipeline()

# Define 
#source
monoB = pipeline.create(dai.node.MonoCamera)
manipB = pipeline.create(dai.node.ImageManip)
# XLinkOut
manipOutB = pipeline.create(dai.node.XLinkOut)
manipOutB.setStreamName('manipBOut')
# Script node
script = pipeline.create(dai.node.Script)
script.setScript("""
    import time
    ctrl = CameraControl()
    # ctrl.setCaptureStill(True)
    while True:
        ctrl.setAutoExposureEnable()

        node.io['out'].send(ctrl)
""")



# Properties
#source
monoB.setBoardSocket(dai.CameraBoardSocket.CAM_C)
monoB.setFps(30)
#display
monoB.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
manipB.setMaxOutputFrameSize(monoB.getResolutionHeight()*monoB.getResolutionWidth()*3)

# Linking
#script -> inputControl
#source -> output ?
xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName('output_stream')

monoB.out.link(xout.input)
script.outputs['out'].link(monoB.inputControl)

#source -> manip
monoB.out.link(manipB.inputImage) 
#manip -> display
manipB.out.link(manipOutB.input)


# Connect to device with pipeline
with dai.Device(pipeline) as dev:
    
    #display queue : 
    showQ_B = dev.getOutputQueue(name=manipOutB.getStreamName(), maxSize=4,blocking=False)
    scriptOutQ_B = dev.getOutputQueue(name=xout.getStreamName(),maxSize=4,blocking=False)


    def read_and_display_img():
        while True:
            if(showQ_B.has()):
                cv2.imshow("camb", showQ_B.get().getCvFrame())
            key = cv2.waitKey(1)

    if (False):
        #display thread
        img_reading_thread= threading.Thread(target=read_and_display_img)
        img_reading_thread.start()  


    while True:

        cv2.imshow('from xout', scriptOutQ_B.get().getCvFrame())
        if cv2.waitKey(1) == ord('q'):
            break
