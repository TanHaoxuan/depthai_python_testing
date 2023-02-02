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
# XLinkIN
xin = pipeline.create(dai.node.XLinkIn)
xin.setStreamName('in')
# XLinkOut
manipOutB = pipeline.create(dai.node.XLinkOut)
manipOutB.setStreamName('manipBOut')

xout = pipeline.create(dai.node.XLinkOut) # xout is for display purpose
xout.setStreamName('output_stream')
# Script node
script = pipeline.create(dai.node.Script)
script.setScript("""
    import time

    data = node.io['in'].get().getData()


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
#source -> output 
monoB.out.link(xout.input)

#xlinkin -> script
xin.out.link(script.inputs['in'])
#script -> inputControl
script.outputs['out'].link(monoB.inputControl)

#source -> manip
monoB.out.link(manipB.inputImage) 
#manip -> display
manipB.out.link(manipOutB.input)


# Connect to device with pipeline
with dai.Device(pipeline) as dev:
    
    #input queue
    inputQ_B = dev.getInputQueue(name=xin.getStreamName())

    #display queue : 
    showQ_B = dev.getOutputQueue(name=manipOutB.getStreamName(), maxSize=4,blocking=False)
    scriptOutQ_B = dev.getOutputQueue(name=xout.getStreamName(),maxSize=4,blocking=False)

    # how to send data Xlink : json
    dict = {'one':1, 'foo': 'bar'}
    print('dict', dict)
    data = json.dumps(dict).encode('utf-8')
    buffer = dai.Buffer()
    buffer.setData(list(data)) #setData is the data we want to send
    inputQ_B.send(buffer)




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
