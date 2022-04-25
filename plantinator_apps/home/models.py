from django.db import models

# Create your models here.
class seedling_process_analysis(models.Model):
	session_name = models.CharField(max_length = 100, unique =  True)
	tot_artichokes_seedlng_imgs = models.IntegerField(default = 0, editable = False)
	good_seedling_quality_qty = models.IntegerField(default = 0, editable = False)
	avrg_seedling_quality_qty = models.IntegerField(default = 0, editable = False)
	bad_seedling_quality_qty = models.IntegerField(default = 0, editable = False)
	good_seedling_quality_prcntg = models.FloatField(default = 0.0, editable = False)
	avrg_seedling_quality_prcntg = models.FloatField(default = 0.0, editable = False)
	bad_seedling_quality_prcntg = models.FloatField(default = 0.0, editable = False) #null = True, blank = True
	
	def __str__(self):
		return self.session_name

class seedling_img_samples(models.Model):
	img_name = models.CharField(max_length = 50, unique = True)
	spa = models.ForeignKey(seedling_process_analysis, on_delete=models.CASCADE)
	#img_file = models.ImageField(null = True, blank = True, upload_to="media", default='/media/defaultimg.jpg')
	img_datetime = models.DateTimeField(auto_now_add = True)
	num_seedling_objs = models.IntegerField(default = 0)

	def __str__(self):
		return self.img_name

class current_SPA_session(models.Model):
	id_field = models.IntegerField(primary_key = True, default = 1)
	current_spa_session_name = models.CharField(max_length = 100, unique = True, default="Default_session")

	def __str__(self):
		return self.current_spa_session_name
