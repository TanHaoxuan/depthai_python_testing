#!/usr/bin/env python3

import cv2
import depthai as dai
import threading

camb_filepath = 'recorded_data/camb_mono.h264'
camc_filepath = 'recorded_data/camc_mono.h264'


# Create pipeline
pipeline = dai.Pipeline()

# Define 
#source
monoB = pipeline.create(dai.node.MonoCamera)
monoC = pipeline.create(dai.node.MonoCamera)
#encoder
veB = pipeline.create(dai.node.VideoEncoder)
veC = pipeline.create(dai.node.VideoEncoder)
#output
veBOut = pipeline.create(dai.node.XLinkOut)
veCOut = pipeline.create(dai.node.XLinkOut)

veBOut.setStreamName('veBOut')
veCOut.setStreamName('veCOut')
#display
manipB = pipeline.create(dai.node.ImageManip)
manipC = pipeline.create(dai.node.ImageManip)
manipOutB = pipeline.create(dai.node.XLinkOut)
manipOutC = pipeline.create(dai.node.XLinkOut)

manipOutB.setStreamName("manipBOut")
manipOutC.setStreamName("manipCOut")



# Properties
#source
monoB.setBoardSocket(dai.CameraBoardSocket.CAM_B)
monoC.setBoardSocket(dai.CameraBoardSocket.CAM_C)
monoB.setFps(30)
monoC.setFps(30)
#encoder
veB.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H264_MAIN)
veC.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H265_MAIN)
#display
monoB.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
manipB.setMaxOutputFrameSize(monoB.getResolutionHeight()*monoB.getResolutionWidth()*3)
monoC.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
manipC.setMaxOutputFrameSize(monoC.getResolutionHeight()*monoC.getResolutionWidth()*3)


# Linking
#source -> encoder
monoB.out.link(veB.input)
monoC.out.link(veC.input)
#encoder -> output
veB.bitstream.link(veBOut.input)
veC.bitstream.link(veCOut.input)

#source -> manip
monoB.out.link(manipB.inputImage) 
monoC.out.link(manipC.inputImage) 
#manip -> display
manipB.out.link(manipOutB.input)
manipC.out.link(manipOutC.input)



# Connect to device and start pipeline
with dai.Device(pipeline) as dev:

    #output queue : store data from output 
    outQ_B = dev.getOutputQueue(name=veBOut.getStreamName(), maxSize=30, blocking=True)
    outQ_C = dev.getOutputQueue(name=veCOut.getStreamName(), maxSize=30, blocking=True)

    #display queue : 
    showQ_B = dev.getOutputQueue(name=manipOutB.getStreamName(), maxSize=4,blocking=False)
    showQ_C = dev.getOutputQueue(name=manipOutC.getStreamName(), maxSize=4,blocking=False)


    def read_and_display_img():
        while True:
            if(showQ_B.has()):
                cv2.imshow("camb", showQ_B.get().getCvFrame())
            if(showQ_C.has()):
                cv2.imshow("camc", showQ_C.get().getCvFrame())
            key = cv2.waitKey(1)

    #display thread
    img_reading_thread= threading.Thread(target=read_and_display_img)
    img_reading_thread.start()

    #main thread
    with open(camb_filepath, 'wb') as file_camb_H264, open(camc_filepath, 'wb') as file_camc_H264:
        print("Recording start.")
        print("Press Ctrl+C to stop recording...")

        while True:

            try:
                # Empty the output queue and store the
                while outQ_B.has():
                    outQ_B.get().getData().tofile(file_camb_H264)

                while outQ_C.has():
                    outQ_C.get().getData().tofile(file_camc_H264)
            except KeyboardInterrupt:
                break
    
    print("To view the encoded data, convert the stream file (.h264/.h265) into a video file (.mp4), using commands below:")
    cmd = "ffmpeg -framerate 30 -i {} -c copy {}"
    print(cmd.format("cam*_mono.h264", "mono_*.mp4"))

