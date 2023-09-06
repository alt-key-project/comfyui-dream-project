# Dream Project Animation Nodes for ComfyUI

This repository contains various nodes for supporting Deforum-style animation generation with ComfyUI. I created these
for my own use (producing videos for my "Alt Key Project" music - 
[youtube channel](https://www.youtube.com/channel/UC4cKvJ4hia7zULxeCc-7OcQ), but I think they should be generic enough 
and useful to many ComfyUI users.

I have demonstrated the use of these custom nodes in this [youtube video](https://youtu.be/pZ6Li3qF-Kk).

## Installation

Run within (ComfyUI)/custom_nodes/ folder:

* git clone https://github.com/alt-key-project/comfyui-dream-project.git
* cd comfyui-dream-project

Then, if you are using the python embedded in ComfyUI:
* (ComfyUI)/python_embedded/python.exe -s -m pip install -r requirements.txt

With your system-wide python:
*  pip install -r requirements.txt

Finally:
* Start ComfyUI.

After startup, a configuration file 'config.json' should have been created in the 'comfyui-dream-project' directory. 
Specifically check that the path of ffmpeg works in your system (add full path to the command if needed).

## Concepts used

These are some concepts used in nodes:

### Frame Counter

The frame counter is an abstraction that keeps track of where we are in the animation - what frame is rendered 
and how does the current frame fit into the current animation.

### Curves

A curve is simply a node that produces a value based on the frame counter (changing over time).

### Palette

A palette is a collection of color values.

### Sequence

A sequence is a full set of animation frames and a corresponding timeline for these frames. The sequence is
created by the 'Image Sequence Saver' node and it may be used to trigger post processing tasks such as generating the 
video file using ffmpeg. These nodes should be seen as a convenience and they are severely limited. Never put sequence 
nodes in parallel - they will not work as intended!

## The nodes
  ### Analyze Palette [Dream]
  Output brightness, red, green and blue averages of a palette. Useful to control other processing.

  ### Beat Curve [Dream]
  Beat pattern curve with impulses at specified beats of a measure.
  
  ### CSV Curve [Dream]
  CSV input curve where first column is frame or second and second column is value.
  
  ### CSV Generator [Dream]
  CSV output, mainly for debugging purposes. First column is frame number and second is value.
  Recreates file at frame 0 (removing and existing content in the file).
  
  ### Common Frame Dimensions [Dream]
  Utility for calculating good width/height based on common video dimensions.
  
  ### FFMPEG Video Encoder [Dream]
  Post processing for animation sequences calling FFMPEG to generate video file.
  
  ### File Count [Dream]
  Finds the number of files in a directory matching specified patterns.
  
  ### Frame Counter (Directory) [Dream]
  Directory backed frame counter, for output directories.
  
  ### Frame Counter (Simple) [Dream]
  Integer value used as frame counter. Useful for testing or if an auto-incrementing primitive is used as a frame 
  counter.
  
  ### Frame Counter Offset [Dream]
  Adds an offset to a frame counter.
  
  ### Image Motion [Dream]
  Node supporting zooming in/out and translating an image.
  
  ### Image Sequence Blend [Dream]
  Post processing for animation sequences blending frame for a smoother blurred effect.
  
  ### Image Sequence Loader [Dream]
  Loads a frame from a directory of images.
  
  ### Image Sequence Saver [Dream]
  Saves a frame to a directory.
  
  ### Image Sequence Tweening [Dream]
  Post processing for animation sequences generating blended in-between frames.
  
  ### Linear Curve [Dream]
  Linear interpolation between two values over the full animation.
  
  ### Noise from Palette [Dream]
  Generates noise based on the colors in a palette.
  
  ### Palette Color Align [Dream]
  Shifts the colors of one palette towards another target palette. If the alignment factor 
  is 0.5 the result is nearly an average of the two palettes. At 0 no alignment is done and at 1 we get a close 
  alignment to the target. Above one we will overshoot the alignment.
  
  ### Palette Color Shift [Dream]
  Multiplies the color values in a palette to shift the color balance or brightness.
  
  ### Sample Image as Palette [Dream]
  Randomly samples pixels from a source image to build a palette from it.
  
  ### Sine Curve [Dream]
  Simple sine wave curve.
 
 ### Other custom nodes
 
 Many of the nodes found in 'WAS Node Suite' are useful the Dream Project Animation nodes - I suggest you install those 
 custom nodes as well!

 ## Examples

 ### Image Motion with Curves

This example should be a starting point for anyone wanting to build with the Dream Project Animation nodes.

[motion-workflow-example](examples/motion-workflow-example.json)

