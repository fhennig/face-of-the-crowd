# ArtSci 2019 Average Face Project

The basic idea is a vertical screen showing a portrait which is an
average of a bunch of faces.  The faces are pictures taken from
visitors of the exhibition.

Besides the screen there is a camera, where people can have their
picture taken and added to the average.


## Motivation

The project is meant to convey the fascinating side of science with
an artistic element.

(There will be more here in the future.)


## Setup / Idea

### Hardware

- FullHD Screen
  - Hopefully provided by the ETHZ
- FullHD camera
  - I need to by that one myself to test
  
### Software

- Needs to display a fullscreen image
- Needs to show a smaller image in the bottom of the frame, which is
  the life image from the camera
- Needs to read out the image data from the camera and show it on the
  screen
- ML part: Needs to extract the face from the picture

## Implementation

Uses OpenCV and [face_recognition](https://github.com/ageitgey/face_recognition).


## Roadmap

- To align the faces, face landmarks need to be extracted. DONE
- Based on the landmarks any rotation of the face can be accounted for. DONE
- Images need to be saved (maybe for a start just with the press of a
  button) and then overlayed (using the landmarks). DONE

- Enhance alignments by using all landmarks as described
  [here](https://www.learnopencv.com/face-morph-using-opencv-cpp-python/).


## Licensing

This project uses a sound from freesound: `bing.wav`, originally
[buttonchime02up.wav](https://freesound.org/people/JustinBW/sounds/80921/),
created by *JustinBW*.
