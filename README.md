# track-the-surf
Tool for tracking blobs in the surfzone. 

## tl;dr
Sequential images are resized, stitched together into video clips and stabilized. Computer vision techniques are then applied to the videos to track the blob progression over time. The goal is to provide inputs for a predictive machine learning model in the form of contours and density as pixels.

## Prepping the images
Drone imagery collected during the SCOPE field experiment and georectified by Brouwer et al. 2015 make up the preliminary data for this project. Images were  compiled  in  the  chronological  order  they  were  captured  and  stitched together  into  a  movie  to  observe  the  dispersion  rates  and  patterns  of  the spill.  This was completed in a series of steps:

- (1) Using `ffmpeg`, the images were stitched together into a movie to show the growth of the spill.  Because two UAVs were used, the resulting movie was discontinuous at the points when the drones were swapped out.  For this reason, the video was manually split into 5 batches of continuous footage.

- (2) After reviewing and splitting the movie into batches, the file size of each image was decreased from 12MP (4000×3000 pixels) to 3MP (2000×1500pixels) in order to stabilize the videos in a shorter period of time. This process also reduces the size and time required to process the video data.

- (3) For each batch of images, `ffmpeg` was used to renumber the images beginning with `0001` before processing the images and rendering them as movies. A total of 5 continuous movies were generated,  each built from about 200 high-resolution sequential images. The file sizes of the generated mp4 movie files ranged from 7.3MB to 19.4MB.

- (4) (4) A video-stabilization tool was used to identify reference points and transform these images into smooth time lapse videos. This was achieved using `Vid.stab` plugged-in with `ffmpeg`. This step was required as the library of raw images, when stitched together, came out unstable and shaky due to being captured by drone imagery. `Vid.stab` targets control points from the images to help create a smoother, more stabilized movie. The transformations that must occur to stabilize the video are detected and then applied to produce a stabilized output video file.
