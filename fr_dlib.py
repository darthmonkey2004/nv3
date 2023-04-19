#This class object is adapted from face_recognition.py ('ageitgey@gmail.com') for use in python_nv (nv.main.detector.py)
#Box order: l, t, r, b (face_recognition used t,r,b,l... may need to adapt?)
#To alter options on the fly (in runtime), parent (detector.py) should set the conf and re-initialize the class. CAN'T DO IT FROM HERE!???
import cv2
from pkg_resources import resource_filename
import dlib
import numpy as np
from PIL import ImageFile
from conf import read_opts
from utils import *
from log import nv_logger

def pose_predictor_large_location():
    return resource_filename(__name__, "models/shape_predictor_68_face_landmarks.dat")

def pose_predictor_small_location():
    return resource_filename(__name__, "models/shape_predictor_5_face_landmarks.dat")

def face_recognition_model_location():
    return resource_filename(__name__, "models/dlib_face_recognition_resnet_model_v1.dat")

def cnn_face_detector_model_location():
    return resource_filename(__name__, "models/mmod_human_face_detector.dat")


log = nv_logger().log_msg

	
class fr_dlib():
	def __init__(self):
		opts = read_opts(0)
		self.face_detector = dlib.get_frontal_face_detector()
		predictor_68_point_model = pose_predictor_large_location()
		self.pose_predictor_large = dlib.shape_predictor(predictor_68_point_model)
		predictor_5_point_model = pose_predictor_small_location()
		self.pose_predictor_small = dlib.shape_predictor(predictor_5_point_model)
		cnn_face_detection_model = pose_predictor_large_location()
		self.cnn_face_detector = dlib.cnn_face_detection_model_v1(cnn_face_detector_model_location())
		face_recognition_model = face_recognition_model_location()
		self.face_encoder = dlib.face_recognition_model_v1(face_recognition_model)
		self.upsamples = opts['detector']['fr_dlib']['upsamples']
		self.model = opts['detector']['fr_dlib']['model']
		self.tolerance = opts['detector']['fr_dlib']['tolerance']
		self.type = opts['detector']['fr_dlib']['type']
		self.pose_predictor = self.set_pose_predictor(self.type)
		

	def set_pose_predictor(self, _type=None):
		if _type is not None:
			self.type = _type
		if self.type == 'large' or _type is None:
			self.pose_predictor = self.pose_predictor_large
		elif self.type == 'small':
			self.pose_predictor = self.pose_predictor_small
		return self.pose_predictor

	def scale_box(self, img, ratio, box):
		return scale_box(img, ratio, box)

		
	def calculate_scale_byratio(self, img_size, r=0.5):
		return calculcate_scale_byratio(img_size, r)

	def calculate_ratio_bysize(self, img_size, target_size):
		return calculate_ratio_bysize(img_size, r)

	def box_to_rect(self, box):
		return dlib.rectangle(box[2], box[3], box[0], box[1])

	def rect_to_box(self, rect):
		return (rect.left, rect.top, rect.right, rect.bottom)

	def constrain_box(self, box, img):
		#constrain box to image dimensions (check r and bo within w and h)
		try:
			l, t, r, b = box[0](), box[1](), box[2](), box[3]()
		except Exception as e:
			data = dir(box)
			#log(f"Tuple probably not rectangle ({box}, data:{data}", 'error')
			l, t, r, b = box
			h, w, c = img.shape
			if b > h:
				b = h - 10
			if r > w:
				r = w - 10
		return l, t, r, b
		
	def face_distance(self, known_encodings, target_encoding):
		if len(known_encodings) == 0:
			log(f"No known encodings loaded!", 'error')
			return np.empty((0))

		else:
			try:
				#TODO: lookup axis, does it determine number of items in array? could I just use len(encodings)?
				return np.linalg.norm(known_encodings - target_encoding, axis=1)
		
			except Exception as e:
				log(f"Error calculating face distance: {e}", 'error')

	def read_img(self, filepath):
		# read image to BGR numpy array. Dlib uses RGB(???), may need conversion
		return cv2.imread(filepath)

	def scale_img(self, img, target_size=None, percent=None):
		return scale_img(img, target_size, percent)

	def calculate_scale(self, size, newsize=None):
		#returns w, h scaled to size provided (300,300) if None
		return calculate_scale(size, newsize)
		
	def _face_locations(self, img):
		if self.model == "cnn":
			self.cnn_face_detector(img, self.upsamples)
		elif self.model == "hog":
			return self.face_detector(img, self.upsamples)



	def face_locations(self, img, upsamples=None, model=None):
		if upsamples is not None:
			self.upsamples = upsamples
		if model is not None:
			self.model = model
		boxes = []
		for face in self._face_locations(img):
			box = self.rect_to_box(face)
			boxes.append(self.constrain_box(box, img))
		return boxes


	#TODO: put in batch face location method
	def _batch_face_locations(self, img):
		log(f"TODO: implement this method!", 'error')
		pass

	def batch_face_locations(self, img):
		log(f"TODO: implement this method!", 'error')
		pass


	
	def _face_landmarks(self, img, face_locations=None):
		if face_locations is None:
			face_locations = self._face_locations(img)
		else:
			if type(face_locations) is tuple:
				face_locations = [face_locations]
			face_locations = [self.box_to_rect(face_location) for face_location in face_locations]
		return [self.pose_predictor(img, face_location) for face_location in face_locations]

	def face_landmarks(self, img, face_locations, _type=None):
		if _type is not None:
			#change model if provided...
			self.type = _type
			#switch the pose predictor model
			self.set_pose_predictor(self.type)
		landmarks = _face_landmarks(img, face_locations)
		landmarks_as_tuples = [[(p.x, p.y) for p in landmark.parts()] for landmark in landmarks]
		if self.type == 'large':
			return [{
				"chin": points[0:17],
				"left_eyebrow": points[17:22],
				"right_eyebrow": points[22:27],
				"nose_bridge": points[27:31],
				"nose_tip": points[31:36],
				"left_eye": points[36:42],
				"right_eye": points[42:48],
				"top_lip": points[48:55] + [points[64]] + [points[63]] + [points[62]] + [points[61]] + [points[60]],
				"bottom_lip": points[54:60] + [points[48]] + [points[60]] + [points[67]] + [points[66]] + [points[65]] + [points[64]]
			} for points in landmarks_as_tuples]
		elif self.type == 'small':
			return [{
				"nose_tip": [points[4]],
				"left_eye": points[2:4],
				"right_eye": points[0:2],
			} for points in landmarks_as_tuples]

	def face_encodings(self, img, boxes=None, passes=None):
		if passes is None:
			#log(f"detector:fr_dlib:face_encodings(): number of passes  not set, defaulting to 1.", 'warning')
			passes = 1
		raw_landmarks = self._face_landmarks(img, boxes)
		return [np.array(self.face_encoder.compute_face_descriptor(img, raw_landmark_set, passes)) for raw_landmark_set in raw_landmarks]

	def compare_faces(self, known_face_encodings, target_encoding, tolerance=None):
		if tolerance is not None:
			self.tolerance = tolerance
		return list(self.face_distance(known_face_encodings, target_encoding) <= self.tolerance)
