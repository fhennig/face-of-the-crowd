# The Face of the Crowd

An interactive installation for the [2019 ArtSci
exhibition](https://artsci.ethz.ch/) at the ETH in Zürich.  A portrait
screen shows a face generated from pictures taken from visitors of the
exhibition.


## Description

The idea behind the project is to convey fascination of technology,
where the individual elements are well understood but the result still
seems magical.

The installation recreates the crowds portrait by combining the
individual viewers features.  A camera takes pictures of the passing
viewers, which are then merged together.  The displayed image adjusts
to the new faces over time, the visitor changes the exhibit by viewing
it.

The merging is based on 68 landmarks in the picture positioned in the
eyes, the eyebrows, the nose, the mouth and chin, which are identified
with facial recognition software.

Each landmark position is morphed towards the average positon for that
landmark, calculated from all pictures.  In this way the individual
pictures are morphed together, forming the face of the crowd.


## Exhibition Setup

At the exhibition, the setup consisted of a large ~ 40" screen in
portrait mode, and next to it a small picture frame prompting people
to put their face in the frame.  Behind the frame was a camera
pointing on the frame.  When the camera triggered, a sound was played.


## References

- OpenCV
- [face_recognition](https://github.com/ageitgey/face_recognition)
- [handling landmarks](https://www.learnopencv.com/face-morph-using-opencv-cpp-python/)


## Licensing

This project uses a sound from freesound: `bing.wav`, originally
[buttonchime02up.wav](https://freesound.org/people/JustinBW/sounds/80921/),
created by *JustinBW*.

The project is licensed unter the MIT license.
