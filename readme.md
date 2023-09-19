# Dream Project Animation Nodes for ComfyUI

This repository contains various nodes for supporting Deforum-style animation generation with ComfyUI. I created these
for my own use (producing videos for my "Alt Key Project" music - 
[youtube channel](https://www.youtube.com/channel/UC4cKvJ4hia7zULxeCc-7OcQ)), but I think they should be generic enough 
and useful to many ComfyUI users.

I have demonstrated the use of these custom nodes in this [youtube video](https://youtu.be/pZ6Li3qF-Kk).

## Installation

### Simple option

You can install Dream Project Animation Nodes using the ComfyUI Manager.

### Manual option

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

## Upgrade

When upgrading, it is good to re-run the pip install command as specified in the install section. This will install any 
new dependencies.

## Configuration

### debug

Setting this to true will enable some trace-level logging.

### ffmpeg.file_extension

Sets the output file extension and with that the envelope used.

### ffmpeg.path 

Path to the ffmpeg executable or just the command if ffmpeg is in PATH.

### ffmpeg.arguments

The arguments sent to FFMPEG. A few of the values are provided by the node:

* %FPS% the target framerate
* %FRAMES% a frame ionput file
* %OUTPUT% output video file path

### encoding.jpeg__quality

Sets the encoding quality of jpeg images.

### ui.top_category

Sets the name of the top level category on the menu. Set to empty string "" to remove the top level. If the top level 
is removed you may also want to disable the category icons to get nodes into existing category folders.

### prepend_icon_to_category / append_icon_to_category

Flags to add a icon before and/or after the category name at each level.

### prepend_icon_icon_to_node / append_icon_icon_to_node

Flags to add an icon before and/or after the node name.

### ui.category_icons

Each key defines a unicode symbol as an icon used for the specified category.

### mpeg_coder.bitrate_factor

This factor allows changing the bitrate to better fit the required quality and codec. A value of 1 is typically 
suitable for H.265.

### mpeg_coder.codec_name

Codec names as specified by ffmpeg. Some common options include "libx264", "libx264" and "mpeg2video".

### mpeg_coder.encoding_threads

Increasing the number of encoding threads in mpegCoder will generally reduce the overall encoding time, but it will also 
increase the load on the computer.

### mpeg_coder.file_extension

Sets the output file extension and with that the envelope used.

### mpeg_coder.max_b_frame

Sets the max-b-frames parameter for as specified in ffmpeg.

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

### Big *** Switch [Dream]
Switch nodes for different type for up to ten inputs.

### Boolean To Float/Int [Dream]
Converts a boolean value to two different numeric values.

### Build Prompt [Dream] (and Finalize Prompt [Dream])
Weighted text prompt builder utility. Chain any number of these nodes and terminate with 'Finalize Prompt'.

### Calculation [Dream]
Mathematical calculation node. Exposes most of the mathematical functions in the python 
[math module](https://docs.python.org/3/library/math.html), mathematical operators as well as round, abs, int, 
float, max and min.

### Compare Palettes [Dream]
Analyses two palettes and produces the quotient for each individual channel (b/a) and brightness.

### CSV Curve [Dream]
CSV input curve where first column is frame or second and second column is value.

### CSV Generator [Dream]
CSV output, mainly for debugging purposes. First column is frame number and second is value.
Recreates file at frame 0 (removing and existing content in the file).

### Common Frame Dimensions [Dream]
Utility for calculating good width/height based on common video dimensions.

### Video Encoder (FFMPEG) [Dream]
Post processing for animation sequences calling FFMPEG to generate video files.

### Video Encoder (mpegCoder) [Dream]
Post processing for animation sequences using the python module mpegCoder with ffmpeg library to generate video files.

### File Count [Dream]
Finds the number of files in a directory matching specified patterns.

### Float/Int/string to Log Entry [Dream]
Logging for float/int/string values.

### Frame Count Calculator [Dream]
Simple utility to calculate number of frames based on time and framerate.

### Frame Counter (Directory) [Dream]
Directory backed frame counter, for output directories.

### Frame Counter (Simple) [Dream]
Integer value used as frame counter. Useful for testing or if an auto-incrementing primitive is used as a frame 
counter.

### Frame Counter Info [Dream]
Extracts information from the frame counter.

### Frame Counter Offset [Dream]
Adds an offset (in frames) to a frame counter.

### Frame Counter Time Offset [Dream]
Adds an offset in seconds to a frame counter.

### Image Brightness Adjustment [Dream]
Adjusts the brightness of an image by a factor.

### Image Color Shift [Dream]
Allows changing the colors of an image with a multiplier for each channel (RGB).

### Image Contrast Adjustment [Dream]
Adjusts the contrast of an image by a factor.

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

### Laboratory [Dream]
Super-charged number generator for experimenting with ComfyUI.

### Log Entry Joiner [Dream]
Merges multiple log entries (reduces noodling).

### Log File [Dream]
The text logging facility for the Dream Project Animation nodes.

### Linear Curve [Dream]
Linear interpolation between two values over the full animation.

### Noise from Area Palettes [Dream]
Generates noise based on the colors of up to nine different palettes, each connected to position/area of the 
image. Although the palettes are optional, at least one palette should be provided.

### Noise from Palette [Dream]
Generates noise based on the colors in a palette.

### Palette Color Align [Dream]
Shifts the colors of one palette towards another target palette. If the alignment factor 
is 0.5 the result is nearly an average of the two palettes. At 0 no alignment is done and at 1 we get a close 
alignment to the target. Above one we will overshoot the alignment.

### Palette Color Shift [Dream]
Multiplies the color values in a palette to shift the color balance or brightness.

### Sample Image Area as Palette [Dream]
Randomly samples a palette from an image based on pre-defined areas. The image is separated into nine rectangular areas 
of equal size and each node may sample one of these.

### Sample Image as Palette [Dream]
Randomly samples pixels from a source image to build a palette from it.

### Saw Curve [Dream]
Saw wave curve.

### Sine Curve [Dream]
Simple sine wave curve.

### Smooth Event Curve [Dream]
Single event/peak curve with a slight bell-shape. 

### String Tokenizer [Dream]
Splits a text into tokens by a separator and returns one of the tokens based on a given index.

### Triangle Curve [Dream]
Triangle wave curve. 

### Triangle Event Curve [Dream]
Single event/peak curve with triangular shape.

### WAV Curve [Dream]
Use an uncompressed WAV audio file as a curve.

### Other custom nodes

Many of the nodes found in 'WAS Node Suite' are useful the Dream Project Animation nodes - I suggest you install those 
custom nodes as well!

## Examples

### Image Motion with Curves

This example should be a starting point for anyone wanting to build with the Dream Project Animation nodes.

[motion-workflow-example](examples/motion-workflow-example.json)

### Image Motion with Color Coherence

Same as above but with added color coherence through palettes.

[motion-workflow-with-color-coherence](examples/motion-workflow-with-color-coherence.json)

### Area Sampled Noise

This flow demonstrates sampling image areas into palettes and generating noise for these areas.

[area-sampled-noise](examples/area-sampled-noise.json)

### Prompt Morphing

This flow demonstrates prompt building with weights based on curves and brightness and contrast control.

[prompt-morphing](examples/prompt-morphing.json)

### Laboratory

This flow demonstrates use of the Laboratory and Logging nodes.

[laboratory](examples/laboratory.json)

## Known issues

### FFMPEG

The call to FFMPEG currently in the default configuration (in config.json) does not seem to work for everyone. The good 
news is that you can change the arguments to whatever works for you - the node-supplied parameters (that probably all need to be in the call)
are:

* -i %FRAMES% (the input file listing frames)
* -r %FPS% (sets the frame rate)
* %OUTPUT% (the path to the video file)

If possible, I will change the default configuration to one that more versions/builds of ffmpeg will accept. Do let me 
know what arguments are causing issues for you!

### Framerate is not always right with mpegCoder encoding node

The mpegCoder library will always use variable frame rate encoding if it is available in the output format. With most 
outputs this means that your actual framerate will differ slightly from the requested one.
