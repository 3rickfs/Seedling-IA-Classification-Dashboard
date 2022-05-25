from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from json import dumps
from django.core.files.storage import FileSystemStorage
from .forms import SPA_Form, SPA_dates
from . models import seedling_process_analysis, current_SPA_session, seedling_img_samples
from django.http import JsonResponse
from django.core import serializers
from django.db.models import F
from django.conf import settings
from datetime import datetime
import random
from PIL import Image, ImageDraw
import os
import requests
import pandas as pd
import json
import numpy as np

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

@login_required(login_url="/login/")
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

	############# Sending the forms and data models #############
	rfile_url = os.path.join(settings.MEDIA_URL, 'questionplant.png')
	dataJSON = dumps(datadict)
	form = SPA_Form()
	datepickers = SPA_dates()
	spa_sessions = seedling_process_analysis.objects.all()
	cspas = current_SPA_session.objects.all()
	if cspas: #and not spa_del:
		cspas = current_SPA_session.objects.get(id_field = 1)
		curr_sess = cspas.current_spa_session_name
		#context['ecd'] = spa_sis_dataJSON(curr_sess) #dataJSON
		try:
			ecd = spa_sis_dataJSON(curr_sess)
			context = {'segment': 'index', 'ecd':ecd, 'tasksq':6, 'rfile_url': rfile_url, 
					   'form': form, 'datepickers':datepickers, 'spa_sessions': spa_sessions, 
					   'current_spa_session': curr_sess,}
		except:
			curr_sess = ""
			context = {'segment': 'index','ecd':dataJSON, 'tasksq':6, 'rfile_url': rfile_url, 
					   'form': form, 'datepickers':datepickers, 'spa_sessions': spa_sessions, 
					   'current_spa_session': curr_sess,}
	else:
		curr_sess = ""
		context = {'segment': 'index','ecd':dataJSON, 'tasksq':6, 'rfile_url': rfile_url, 
				   'form': form, 'datepickers':datepickers, 'spa_sessions': spa_sessions, 
				   'current_spa_session': curr_sess,}
	##############################################################

	# To process the image uploaded by the user
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

		#Making predictions with REST API
		print("Seding POST request!")
		URL = "http://127.0.0.1:7000/seedling_image/"

		furl = "http://" + request.get_host() + file_url
		#http://127.0.0.1:8000/media/artichoke21_Nz7KeVg.jpeg
		print(f"furl: {furl}")
		#PARAMS = {'url':furl}
		#files = {'obvius_session_id': '72c2b6f406cdabd578c5fd7598557c52'}
		files = {'url':str(furl)}
		###########################REQUEST TO REST API########################
		r = requests.post(url = URL, data = files)
		######################################################################
		#r = requests.post(url = URL, files = dict(url=furl))
		
		#Extracting data in json format
		apidata = r.json()
		#print(f"json Response from API: {apidata}")
		apidatalist = json.loads(apidata)
		#print(f"list Response from API: {apidatalist}")
		apidata_df = pd.DataFrame(data=apidatalist, columns=['class','x','y','w','h','confidence'])
		apidata_df = apidata_df.astype({'class': np.int32})
		print(f"apidata_df: {apidata_df}")

		#Open the image
		imgpath = os.path.join(settings.MEDIA_ROOT, file)

		simg = Image.open(imgpath)
		for i in range(len(apidata_df)):
			if apidata_df.loc[i,'class'] != 0:
				draw = ImageDraw.Draw(simg)
				x1, y1 = apidata_df.loc[i,'x'], apidata_df.loc[i,'y']
				x2, y2 = x1 + apidata_df.loc[i,'w'], y1 + apidata_df.loc[i,'h']
				#draw.rectangle((200, 100, 300, 200), outline = "yellow", width = 2)
				if apidata_df.loc[i,'class'] == 1: oln = "red"
				if apidata_df.loc[i,'class'] == 2: oln = "yellow"
				if apidata_df.loc[i,'class'] == 3: oln = "green"
				draw.rectangle((x1, y1, x2, y2), outline = oln, width = 2)
			else:
				print("There was not detected seedlings")
		nname = file.split(".")[0] + "r.jpg"
		output_path = os.path.join(settings.MEDIA_ROOT, nname)
		simg.save(output_path)
		rfile_url = os.path.join(settings.MEDIA_URL, nname)
		print(f"rfile_url: {rfile_url}")
		context['rfile_url'] = rfile_url

		print(apidata_df['class'].eq(3).sum())

		#if cspas.current_spa_session_name != "Default_session":
		#Updating session data after image processing
		if cspas:
			print(f"all: {current_SPA_session.objects.all()}")
			cspas = current_SPA_session.objects.get(id_field = 1)
			curr_sess = cspas.current_spa_session_name
			session = seedling_process_analysis.objects.filter(session_name = curr_sess)
			session.update(tot_artichokes_seedlng_imgs = F('tot_artichokes_seedlng_imgs') + 1)
			#session.update(good_seedling_quality_qty = F('good_seedling_quality_qty') + random.choice(list1))
			session.update(good_seedling_quality_qty = F('good_seedling_quality_qty') + int(apidata_df['class'].eq(3).sum()))
			#session.update(avrg_seedling_quality_qty = F('avrg_seedling_quality_qty') + random.choice(list1))
			session.update(avrg_seedling_quality_qty = F('avrg_seedling_quality_qty') + int(apidata_df['class'].eq(2).sum()))
			#session.update(bad_seedling_quality_qty = F('bad_seedling_quality_qty') + random.choice(list1))
			session.update(bad_seedling_quality_qty = F('bad_seedling_quality_qty') + int(apidata_df['class'].eq(1).sum()))

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
			sis = seedling_img_samples(id = None, img_name = upload.name, spa = spa, img_datetime = datetime.now(), num_seedling_objs = int(apidata_df[apidata_df['class']>0]['class'].count()))
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

@login_required(login_url="/login/")
def post_SPA(request):
	#request should be ajax and method should be POST
	if request.is_ajax and request.method == "POST":
		#get the form data
		form = SPA_Form(request.POST)
		formdates = SPA_dates(request.POST)

		#save the data after fetch object in instance
		if form.is_valid() and formdates.is_valid():
			instance = form.save(commit=False)
			instance.spa_session_idate = formdates.cleaned_data['initial_date_field']
			instance.spa_session_fdate = formdates.cleaned_data['final_date_field']
			instance.save()

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
			
			#Updating current_spa_session_name model with the current session name and about dates to filter seedling process analysis model
			cspas = current_SPA_session.objects.filter(pk=1)
			cspas.update(current_spa_session_name = form.cleaned_data['session_name'])
			
			#cspas.update(spa_session_idate = formdates.cleaned_data['initial_date_field'])
			#cspas.update(spa_session_fdate = formdates.cleaned_data['final_date_field'])

			print(f"Session_name: {form.cleaned_data['session_name']}")
			#serialize in new friend object in json
			ser_instance = serializers.serialize('json', [ instance, ])
			#ser_dateinstance = serializers.serialize('json', [ formdates.cleaned_data['initial_date_field'], formdates.cleaned_data['initial_date_field']])
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

#This screen for guests
@login_required(login_url="/login/")
def dashboard_admin(request):
	#context = {'segment': 'dashboard_invitado'}
	context = {}
	load_template = request.path.split('/')[-1]

	#if load_template == 'admin':
	#	return HttpResponseRedirect(reverse('admin:index'))
	context['segment'] = load_template

	return render(request,'home/dashboard_admin.html', context)