# track-the-surf
Tool for tracking blobs in the surfzone. 

## tl;dr
Sequential images are resized, stitched together into video clips and stabilized. Computer vision techniques are then applied to the videos to track the blob progression over time. The goal is to provide inputs for a predictive machine learning model in the form of contours and density as pixels. All straight from the comfort of your terminal!

## Prepping the images
Drone imagery collected during the SCOPE field experiment and georectified by Brouwer et al. 2015 make up the preliminary data for this project. Images were  compiled  in  the  chronological  order  they  were  captured  and  stitched together  into  a  movie  to  observe  the  dispersion  rates  and  patterns  of  the spill.  This was completed in a series of steps:

- (1) Using `ffmpeg`, the images were stitched together into a movie to show the growth of the spill using this command:  
```
ffmpeg -f image2 -s 1000x750 -i img-%04d.JPG -vcodec libx264 -crf 25 -pix_fmt yuv420p SCOPEraw.mp4
```
where `SCOPEraw.mp4` is the output movie file. Because two UAVs were used, the resulting movie was discontinuous at the points when the drones were swapped out.  For this reason, the video was manually split into 5 batches of continuous footage. 

- (2) After reviewing and splitting the movie into batches, the command below decreased the file size of each image from 12MP (4000×3000 pixels) to 3MP (2000×1500pixels) in order to stabilize the videos in a shorter period of time. This process also reduces the size and time required to process the video data with computer vision techniques, to follow.
```
ffmpeg -i img-%04d.JPG -vf scale=2000:1500 output-%04d.jpg
```

- (3) For each batch of images, `ffmpeg` was used to renumber the images beginning with *0001* before processing the images and rendering them as movies, as this is the default starting index for image processing with `ffmpeg`. A total of 6 continuous movies were generated,  each built from about 200 high-resolution sequential images. The file sizes of the generated mp4 movie files ranged from 7.3MB to 19.4MB. The following code runs through the images in a batch and renumbers them, so the images of each batch are numbered from *0001*:
```
#!/bin/bash
a=1
for file in *.jpg
    do
        new=$(printf "output-%04d.jpg" "$a")
        mv -i -- "$file" "$new"
        let a=a+1
    done
```
Then each continuous batch of images was rendered as a movie:
```
ffmpeg -f image2 -s 1000x750 -i output-%04d.JPG -vcodec libx264 -crf 25 -pix_fmt yuv420p batch1.mp4
```

- (4) A video-stabilization tool was used to identify reference points and transform these images into smooth time lapse videos. This was achieved using `Vid.stab` plugged-in with `ffmpeg`. This step was required as the library of raw images, when stitched together, came out unstable and shaky due to being captured by drone imagery. `Vid.stab` targets control points from the images to help create a smoother, more stabilized movie. To produce a stabilized output video file, the code below identifies the transformations that must occur to stabilize the video, and applies them with the second command:
```
ffmpeg -i batch1.mp4 -vf vidstabdetect -f null -
ffmpeg -i batch1.mp4 -vf vidstabtransform=smoothing=5:input="transforms.trf" batch1-stabilized.mp4
```
A side-by-side comparison of the original and stabilized videos can be created with this command (found on a forum [here](http://ffmpeg-users.933282.n4.nabble.com/Merge-two-videos-into-one-with-side-by-side-composition-td4659527.html)):
```
ffmpeg -i batch1.mp4 -i batch1-stabilized.mp4 -filter_complex "[0:v:0]pad=iw*2:ih[bg]; [bg][1:v:0]overlay=w" compare1.mp4
```
