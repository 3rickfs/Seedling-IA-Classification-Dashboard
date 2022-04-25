from django.shortcuts import render
from json import dumps
from django.core.files.storage import FileSystemStorage
from .forms import SPA_Form
from . models import seedling_process_analysis, current_SPA_session, seedling_img_samples
from django.http import JsonResponse
from django.core import serializers
from django.db.models import F
from django.conf import settings
from datetime import datetime
import random
from PIL import Image, ImageDraw
import os

list1 = [2, 5, 8, 12, 23, 16, 19, 20, 4, 1, 13, 14]
plist = [0.1, 0.6, 0.2, 0.7, 0.52, 0.23, 0.92, 0.81]

def spa_sis_dataJSON(curr_sess):
	spa = seedling_process_analysis.objects.get(session_name = curr_sess)
	sis_set = seedling_img_samples.objects.filter(spa= spa)
	sis_labels, sis_data = [], []
	for i, sis in enumerate(sis_set):
		sis_data.append(sis.num_seedling_objs)
		sis_labels.append("img_" + str(i))

	totseedlings = spa.good_seedling_quality_qty + spa.avrg_seedling_quality_qty + spa.bad_seedling_quality_qty
	qq = [spa.good_seedling_quality_qty, spa.avrg_seedling_quality_qty, spa.bad_seedling_quality_qty]
	if totseedlings > 0:
		qqp = [(spa.good_seedling_quality_prcntg/totseedlings) * 100, 
			   (spa.avrg_seedling_quality_prcntg/totseedlings) * 100, 
			   (spa.bad_seedling_quality_prcntg/totseedlings) * 100]
	else:
		qqp = [0, 0, 0]

	datadict = {
		'exchda': [1, 20, 30, 40, 50, 60, 50, 40, 30, 20, 10, 1],
		'tasidata': sis_data,
		'tasilabel': sis_labels,
		'dasqdata': qq,
		'dasqlabel': ['good', 'avrg', 'bad'],
		'dasqpdata': qqp,
		'dasqplabel': ['good', 'avrg', 'bad'],
	}
	dataJSON = dumps(datadict)

	return dataJSON

def index(request):
	spa_del = False		

	#dummy data in case there is no SPA session initated
	datadict = {
		'exchda': [1, 20, 30, 40, 50, 60, 50, 40, 30, 20, 10, 1],
		'tasidata': [0],
		'tasilabel': ['-'],
		'dasqdata': [0, 0, 0],
		'dasqlabel': ['good', 'avrg', 'bad'],
		'dasqpdata': [0, 0, 0],
		'dasqplabel': ['good', 'avrg', 'bad'],
	}

	dataJSON = dumps(datadict)
	form = SPA_Form()
	spa_sessions = seedling_process_analysis.objects.all()
	cspas = current_SPA_session.objects.all()
	if cspas: #and not spa_del:
		cspas = current_SPA_session.objects.get(id_field = 1)
		curr_sess = cspas.current_spa_session_name
		#context['ecd'] = spa_sis_dataJSON(curr_sess) #dataJSON
		context = {'segment': 'index','ecd':spa_sis_dataJSON(curr_sess), 'tasksq':6, 'form': form, 'spa_sessions': spa_sessions, 'current_spa_session': curr_sess,}
	else:
		curr_sess = ""
		context = {'segment': 'index','ecd':dataJSON, 'tasksq':6, 'form': form, 'spa_sessions': spa_sessions, 'current_spa_session': curr_sess,}

	#if request.method == 'POST':
	#	form = SPA_Form(request.POST)
	#	print(form['session_name'].data)

		#unbound_form['subject'].data
		#if form.is_valid():
		#	form.save()

	if request.method == 'POST' and request.FILES['upload']:
		#cspas = current_SPA_session.objects.filter(id_field=1)
		#cspas = current_SPA_session.objects.all()

		upload = request.FILES['upload']
		fss = FileSystemStorage()
		print(f"upload: {upload}")
		file = fss.save(upload.name, upload)
		print(f"file: {file}")
		file_url = fss.url(file)
		context['file_url'] = file_url
		print(f"file_url: {file_url}")


		#Open the image
		imgpath = os.path.join(settings.MEDIA_ROOT, file)

		simg = Image.open(imgpath)
		draw = ImageDraw.Draw(simg)
		draw.rectangle((200, 100, 300, 200), outline = "yellow", width = 2)
		nname = file.split(".")[0] + "r.jpg"
		output_path = os.path.join(settings.MEDIA_ROOT, nname)
		simg.save(output_path)
		rfile_url = os.path.join(settings.MEDIA_URL, nname)
		print(f"rfile_url: {rfile_url}")
		context['rfile_url'] = rfile_url

		#if cspas.current_spa_session_name != "Default_session":
		if cspas:
			print(f"all: {current_SPA_session.objects.all()}")
			cspas = current_SPA_session.objects.get(id_field = 1)
			curr_sess = cspas.current_spa_session_name
			session = seedling_process_analysis.objects.filter(session_name = curr_sess)
			session.update(tot_artichokes_seedlng_imgs = F('tot_artichokes_seedlng_imgs') + 1)
			session.update(good_seedling_quality_qty = F('good_seedling_quality_qty') + random.choice(list1))
			session.update(avrg_seedling_quality_qty = F('avrg_seedling_quality_qty') + random.choice(list1))
			session.update(bad_seedling_quality_qty = F('bad_seedling_quality_qty') + random.choice(list1))
			totseedlings = session[0].good_seedling_quality_qty + session[0].avrg_seedling_quality_qty + session[0].bad_seedling_quality_qty
			print(f"totseedlings: {totseedlings}")
			session.update(good_seedling_quality_prcntg = round((session[0].good_seedling_quality_qty/totseedlings)*100,2))
			session.update(avrg_seedling_quality_prcntg = round((session[0].avrg_seedling_quality_qty/totseedlings)*100,2))
			session.update(bad_seedling_quality_prcntg = round((session[0].bad_seedling_quality_qty/totseedlings)*100,2))
			#session.update(good_seedling_quality_prcntg = F('good_seedling_quality_qty')/(F('good_seedling_quality_qty')+F('avrg_seedling_quality_qty')+F('bad_seedling_quality_qty')))
			#session.update(avrg_seedling_quality_prcntg = F('avrg_seedling_quality_qty')/(F('good_seedling_quality_qty')+F('avrg_seedling_quality_qty')+F('bad_seedling_quality_qty')))
			#session.update(bad_seedling_quality_prcntg = F('bad_seedling_quality_qty')/(F('good_seedling_quality_qty')+F('avrg_seedling_quality_qty')+F('bad_seedling_quality_qty')))

			context['current_spa_session'] = curr_sess

			#Create a new seedling img sample object and save it
			spa = seedling_process_analysis.objects.get(session_name = curr_sess)
			sis = seedling_img_samples(id = None, img_name = upload.name, spa = spa, img_datetime = datetime.now(), num_seedling_objs = random.choice(list1))
			sis.save()

			print(f"spa: {spa}")
			sis_set = seedling_img_samples.objects.filter(spa= spa)
			print(f"sis_set: {sis_set}")
			#allsis = seedling_img_samples.objects.all()
			#print(f"allsis: {allsis}")
			sis_labels = []
			sis_data = []
			for i, sis in enumerate(sis_set):
				sis_data.append(sis.num_seedling_objs)
				sis_labels.append("img_" + str(i))
			print(f"sis_labels: {sis_labels}")
			print(f"sis_data: {sis_data}")
			

			#session.tot_artichokes_seedlng_imgs
			qq = [session[0].good_seedling_quality_qty, session[0].avrg_seedling_quality_qty, session[0].bad_seedling_quality_qty]
			qqp = [session[0].good_seedling_quality_prcntg, session[0].avrg_seedling_quality_prcntg, session[0].bad_seedling_quality_prcntg]

			datadict = {
				'exchda': [1, 20, 30, 40, 50, 60, 50, 40, 30, 20, 10, 1],
				'tasidata': sis_data,
				'tasilabel': sis_labels,
				'dasqdata': qq,
				'dasqlabel': ['good', 'avrg', 'bad'],
				'dasqpdata': qqp,
				'dasqplabel': ['good', 'avrg', 'bad'],
			}
			dataJSON = dumps(datadict)
			context['ecd'] = dataJSON

			#print(f"cspas: {cspas.current_spa_session_name}")

		return render(request,'home/index.html', context)
	
	return render(request, 'home/index.html', context)


def post_SPA(request):
	#request should be ajax and method should be POST
	if request.is_ajax and request.method == "POST":
		#get the form data
		form = SPA_Form(request.POST)
		#save the data after fetch object in instance
		if form.is_valid():
			instance = form.save()
			#bound_form['subject'].data
			#reporter = Reporters.objects.filter(name='Tintin')
			#reporter.update(stories_filed=F('stories_filed') + 1)
			#session = seedling_process_analysis.objects.filter(session_name='Test_session_2')
			#session.update(bad_seedling_quality_qty=F('bad_seedling_quality_qty') + 1)

			cspas = current_SPA_session.objects.all()
			if not cspas:
				print("Negated cspas")
				cspas = current_SPA_session.objects.create(id_field=1, current_spa_session_name="Default_session")
				cspas.save()
			
			cspas = current_SPA_session.objects.filter(pk=1)
			cspas.update(current_spa_session_name = form.cleaned_data['session_name'])

			print(f"Session_name: {form.cleaned_data['session_name']}")
			#serialize in new friend object in json
			ser_instance = serializers.serialize('json', [ instance, ])
			#send to client side
			#cspas = current_SPA_session.objects.get(id_field = 1)
			#return JsonResponse({"instance": ser_instance, "currspasess": cspas.current_spa_session_name}, status=200)
			#return JsonResponse({"instance": ser_instance}, status=200)
			#return JsonResponse({"instance": ser_instance, "data":dataJSON}, status=200)
			return JsonResponse({"instance": ser_instance, "tasidata": [0], "tasilabel": ['-']}, status=200)
		else:
			#some form errors occured
			return JsonResponse({"error": form.errors}, status=400)

	if request.is_ajax and request.method == "GET":
		#get the form data
		query = request.GET
		#Display query data
		print(query)
		records = seedling_process_analysis.objects.all()
		records.delete()
		seedling_img_samples.objects.all().delete()
		#spa_del = True
		print("All data was deleted")
		cspas = current_SPA_session.objects.filter(id_field = 1)
		cspas.update(current_spa_session_name="Empty")
		ser_instance = {"msg":"Operation was completed"}
		return JsonResponse({"instance": ser_instance}, status=200)


	#some error occured
	return JsonResponse({"error": ""}, status=400)