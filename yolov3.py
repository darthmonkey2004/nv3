import mxnet as mx
from gluoncv import model_zoo, data,utils

class yolov3:
	def __init__(self):
		self.net = model_zoo.get_model('yolo3_darknet53_voc', pretrained=True)

	@staticmethod
	def preprocess(image):
		return data.transforms.presets.yolo.transform_test(mx.ndarray.array(image), short=512)


	def get_object_labels(self, class_ids, scores, score_th=0.5):
		class_ids = class_ids[0].asnumpy().reshape(1, -1)
		scores = scores[0].asnumpy().reshape(1, -1)
		selected_class_ids = class_ids[scores > score_th]
		return [self.net.classes[int(class_id)] for class_id in selected_class_ids]

	def detect_objects(self, image):
		x, img = self.preprocess(image)
		class_ids, scores, bboxs = self.net(x)
		return class_ids, scores, bboxs

	def __call__(self, *args, **kwargs):
		image = kwargs.get('image')
		class_ids, scores, _ = self.detect_objects(image)
		labels = self.get_object_labels(class_ids, scores)
		return labels
