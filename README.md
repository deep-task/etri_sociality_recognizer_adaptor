## 1. etri_sociality_recognizer_adaptor

## 2. Package Summary

This package provides remote interfaces to M2-1 module via TCP socket. This package transmits a stream of images to M2-1 and receives sociality recognition results in the form of JSON message. The result JSON message is published via a ROS topic.

### 2.1 Maintainer status: developed

### 2.2 Maintainer:

Minsu Jang (minsu AT etri DOT re DOT kr), Jaeyoon Jang (jangjy AT etri DOT re DOT kr), Hosub Yoon (yoonhs AT etri DOT re DOT kr)

### 2.3 Author:

Jaeyoon Jang (jangjy AT etri DOT re DOT kr), Hosub Yoon (yoonhs AT etri DOT re DOT kr), Minsu Jang (minsu AT etri DOT re DOT kr)

### 2.4 License (optional): 

### 2.5 Source

https://github.com/deep-task/etri_sociality_recognizer_client

## 3. Overview

The overall process of interactions between this adaptor and M2-1 module is as follows:

1. [etri_sociality_recognizer_adaptor] creates a server socket.
2. [etri_sociality_recognizer] connects to this adaptor via a socket.
3. [etri_sociality_recognizer_adaptor] begins to send an image obtained from an image topic.
4. [etri_sociality_recognizer]
   - receives an image from this adaptor and performs recognition.
   - sends to this adaptor a JSON message containing a set of recognition results including:
     - face detection
     - facial landmark detection
     - age/gender/facial pose detection
     - social action recognition
     - social attribute recognition (long-term observation data)
5. [etri_sociality_recognizer_adaptor] publishes the received JSON message via a recognitionResult topic.

## 4. Installation

1. Clone this repository into a ROS workspace.

   ```
   git clone https://github.com/deep-task/etri_sociality_recognizer_adaptor.git
   ```

2. Configure.

   - Configure the name of the image topic by modifying the value of `Color_Image_Topic` argument inside `launch/bringup.launch`
     - Default topic name is `/webcam/image_raw`
   - Configure the server IP address and the port number by modifying the source of `etri_client_node.py`.
     - At line 142 ~ 143, `HOST` and `PORT` values are set. You must set these numbers properly.

3. Build the packages including this one.

   ```
   catkin build
   ```

4. Run!

   - First, you have to install `etri_sociality_recognizer` on Jetson Xavier NX. Please see the instructions at the following repository.

     - https://github.com/deep-task/etri_sociality_recognizer.git

   - Second, run this adaptor! (This adaptor is a socket server.)

     ```
     roslaunch etri_sociality_recognizer_adaptor bringup.launch
     ```

   - Third, run the `etri_sociality_recognizer`. (refer to the instructions at the repository!)

## 5. Interfaces

### Input/Subscribed Topics

- /Color_Image (sensor_msgs/Image)

### Output/Published Topics

* /recognitionResult (std_msgs/String)
  * The topic outputs a JSON formatted string.
  * A sample message is as follows. The meaning of each field is self-explanatory.

```
{
  "encoding" : "UTF-8",
  "header" :
  {                     
      "content" : [ "human_recognition" ],
      "source" : "ETRI",
      "target" : [ "UOA", "UOS" ],
      "timestamp" : 0
  },
  "human_recognition" :
  [
    {
      "age" : 51.470279693603516,
      "face_roi" : {
            "x1" : 189,
            "x2" : 380,
            "y1" : 249,
            "y2" : 440
      },
      "gender" : 1,                          // 0: female, 1: male
      "glasses" : false,
      "headpose" : {                        
            "pitch" : -0.66468393802642822,
            "roll" : 8.6534614562988281,
            "yaw" : -7.5606122016906738
      },
      "id" : 0,                          // track id (currently not used)
      "name" : "",                       // identification result (currently not used)
      "social_action" : -1,              // -1: not recognized,
                                         //  0: bite nail,                                             
                                         //  1: covering mouth with hands,
                                         //  2: cheering up!, 3: finger heart sign,
                                         //  4: OK sign, 5: crossing arms, 6: neutral
                                         //  7: picking ears,
                                         //  8: resting chin on a hand,
                                         //  9: scratching head, 10: shake hands 
                                         // 11: a thumb up, 12: touching nose
                                         // 13: waving hand, 14: bowing 
     "gaze": 0,                          //  0: aversion, 1: contact
     "longterm_tendency" : {
            "passive" : 0,
            "neutral" : 0,
            "active : 0
      },
      "longterm_habit" : -1              // Habit behavior index
                                         // same as social_action              
     }
  ]}
```

