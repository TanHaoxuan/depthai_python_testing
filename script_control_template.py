#!/usr/bin/env python3
import cv2
import depthai as dai
import threading



# Create pipeline
pipeline = dai.Pipeline()



# Define 
#camera node
monoB = pipeline.create(dai.node.MonoCamera)
#XLinkIN node
xin = pipeline.create(dai.node.XLinkIn)
xin.setStreamName('in')
#XLinkOut node
xout = pipeline.create(dai.node.XLinkOut) # xout is for display purpose
xout.setStreamName('output_stream')
# script node
script = pipeline.create(dai.node.Script)



# Properties
#camera node
monoB.setBoardSocket(dai.CameraBoardSocket.CAM_C)
monoB.setFps(30)
monoB.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
#script node
script.setScript("""
    import time

    data = node.io['in'].get().getData()
    print(data)


    ctrl = CameraControl()
    # ctrl.setCaptureStill(True)
    while True:
        ctrl.setAutoExposureEnable()

        node.io['out'].send(ctrl)
""")



# Linking
#XLinkIn -> script
xin.out.link(script.inputs['in'])
#script -> inputControl
script.outputs['out'].link(monoB.inputControl)
#camera -> output 
monoB.out.link(xout.input)



# Connect to device with pipeline
with dai.Device(pipeline) as dev:
    
    #input queue
    inputQ_B = dev.getInputQueue(name=xin.getStreamName())

    #display queue : 
    outputQ_B = dev.getOutputQueue(name=xout.getStreamName(),maxSize=4,blocking=False)

    # how to send data Xlink : json
    # dict = {'one':1, 'foo': 'bar'}
    # print('dict', dict)
    # data = json.dumps(dict).encode('utf-8')
    buffer = dai.Buffer()
    # buffer.setData(list(data)) #setData is the data we want to send
    buffer.setData(int(36))
    inputQ_B.send(buffer)



    while True:

        cv2.imshow('from xout', outputQ_B.get().getCvFrame())
        if cv2.waitKey(1) == ord('q'):
            break
