#!/usr/bin/python3

#################################################################################################
# Este codigo foi desenvolvido por Marco Teixeira: mantonio.t91@gmail.com 
#################################################################################################

import rospy
import cv2
import mediapipe as mp
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from mediapipe_holistic_ros.msg import  MediaPipeHolistic
from mediapipe_holistic_ros.msg  import  MediaPipePose

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic
mp_hands = mp.solutions.hands

#####
input_usb_cam_topic = rospy.get_param("/mediapipe_holistic_ros/input_usb_cam_topic","/usb_cam/image_raw")
output_image_topic = rospy.get_param("/mediapipe_holistic_ros/output_image_topic","/mediapipe_holistic/output_image")
output_mediapipe_topic = rospy.get_param("/mediapipe_holistic_ros/output_mediapipe_topic","/MediaPipePose/holistic/landmarks")
pub_landmark_output = rospy.get_param("/mediapipe_holistic_ros/pub_landmark_output",True)
pub_image_output = rospy.get_param("/mediapipe_holistic_ros/pub_image_output",True)
view_image = rospy.get_param("/mediapipe_holistic_ros/open_view_image",True)
#####


def apply_landmark(image, results):     
        if (pub_image_output == True or view_image == True):
                # Draw landmark annotation on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                mp_drawing.draw_landmarks(
                        image,
                        results.face_landmarks,
                        mp_holistic.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_contours_style())
                mp_drawing.draw_landmarks(
                        image,
                        results.pose_landmarks,
                        mp_holistic.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles
                        .get_default_pose_landmarks_style())
                mp_drawing.draw_landmarks(
                        image,
                        results.right_hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())       
                mp_drawing.draw_landmarks(
                        image,
                        results.left_hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                        
        if (pub_image_output == True):
                image_message = bridge.cv2_to_imgmsg(image, encoding="passthrough")
                publisher_output_image.publish(image_message) 
        
        if (view_image == True):
                cv2.imshow('MediaPipe Holistic', cv2.flip(image, 1))
                if cv2.waitKey(5) & 0xFF == 27:
                        print("OK")                               
        return image        
                             
def pub_results(results):
        if (pub_landmark_output == True):
                landmarks = MediaPipeHolistic() 

                #face_landmarks
                if results.face_landmarks:
                        p_id = 0
                        for i in results.face_landmarks.landmark:
                                pose = MediaPipePose()
                                pose.id = p_id
                                pose.x = i.x
                                pose.y = i.y
                                pose.z = i.z
                                p_id += 1
                                landmarks.face_landmarks.append(pose)
                #left_hand_landmarks
                if results.left_hand_landmarks:
                        p_id = 0
                        for i in results.left_hand_landmarks.landmark:
                                pose = MediaPipePose()
                                pose.id = p_id
                                pose.x = i.x
                                pose.y = i.y
                                pose.z = i.z
                                p_id += 1
                                landmarks.left_hand_landmarks.append(pose)  
                                
                #right_hand_landmarks
                if results.right_hand_landmarks:
                        p_id = 0
                        for i in results.right_hand_landmarks.landmark:
                                pose = MediaPipePose()
                                pose.id = p_id
                                pose.x = i.x
                                pose.y = i.y
                                pose.z = i.z
                                p_id += 1
                                landmarks.right_hand_landmarks.append(pose) 
                                
                                
                #pose_landmarks
                if results.pose_landmarks:
                        p_id = 0
                        for i in results.pose_landmarks.landmark:
                                pose = MediaPipePose()
                                pose.id = p_id
                                pose.x = i.x
                                pose.y = i.y
                                pose.z = i.z
                                pose.visibility = i.visibility
                                p_id += 1
                                landmarks.pose_landmarks.append(pose) 
                                
                #pose_world_landmarks
                if results.pose_world_landmarks:
                        p_id = 0
                        for i in results.pose_world_landmarks.landmark:
                                pose = MediaPipePose()
                                pose.id = p_id
                                pose.x = i.x
                                pose.y = i.y
                                pose.z = i.z
                                pose.visibility = i.visibility
                                p_id += 1
                                landmarks.pose_world_landmarks.append(pose)                 
                                                        
                publisher_output_mediapipe.publish(landmarks) 
        

if __name__ == '__main__':
        rospy.init_node('MediaPiPeHolistic')
        
        #Global Topics
        bridge = CvBridge()
        
        #Sub and Pub
        publisher_output_image = rospy.Publisher(output_image_topic, Image)
        publisher_output_mediapipe = rospy.Publisher(output_mediapipe_topic, MediaPipeHolistic)
        
        
        with mp_holistic.Holistic(
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as holistic:
          while not rospy.is_shutdown():
                try:
                        data = rospy.wait_for_message(input_usb_cam_topic, Image, timeout=10)
                        image = bridge.imgmsg_to_cv2(data, desired_encoding='bgra8')
                except:
                        print("Image read error")
                        continue                
                
                #apply holistic
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)
                
                #apply landmark
                image = apply_landmark(image, results)  
                pub_results(results)
                   
             

