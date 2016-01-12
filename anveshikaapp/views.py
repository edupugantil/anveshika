from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from anveshikaapp.forms import UserForm, UserAuthForm
from django.template import RequestContext
from anveshikaapp.models import *
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from anveshikaapp.forms import *
from django.conf import settings
from django.db import connection
import os,sys,re,vcf



# Create your views here.
@login_required
def home(request):
  return render(request, 'base.html')
  
def login_user(request):
  params = {}
  msg=None
  if request.method=='POST':
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username,password=password)
    if user is not None:
        # the password verified for the user
        if user.is_active:
            login(request, user)
            msg = "User is valid, active and authenticated"
            return redirect('anveshikaapp.home')
        else:
            msg = "The password is valid, but the account has been disabled!"
    else:
        # the authentication system was unable to verify the username and password
        msg = "The username and password were incorrect."
  params['msg'] = msg
  return render(request, 'login.html', params)

def logout_user(request):
  logout(request)
  return redirect('anveshikaapp.home')

def register(request):
	registered = False
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		userauth_form = UserAuthForm(data=request.POST)
		if user_form.is_valid():
			username = request.POST['username']
			first = request.POST['first_name']
			last = request.POST['last_name']
			password = request.POST['password']
			user = User.objects.create_user(username,password)
			user.first_name = first
			user.last_name = last
			user.save()
			registered = True
   
	else:
		user_form = UserForm()
		userauth_form = UserAuthForm()


	return render(request,'register.html',{'user_form': user_form,'userauth_form': userauth_form, 'registered': registered})
	
	
@login_required
def upload(request):
	params = {}
	msg = None
	if request.method=="POST":
		img = UploadForm(request.POST, request.FILES)		
		if img.is_valid():
			name = request.FILES['img'].name
			#print(name)
			img.save()	
			if name.endswith('.csv'):
				infile = open(os.path.join(settings.MEDIA_ROOT,'vcffiles',name),'r')
				for line in infile:
					if(re.search(r'# Ts/Tv : All',line)):
						line = next(infile)
						line = next(infile)
						if(re.search(r'Sample',line)):
							#line = next(infile)
							sampleName = line.split(",")
							#print(sampleName)
							line = next(infile)
							transitions = line.split(",")
							#print(transitions)
							line = next(infile)
							transversions = line.split(",")
							#print(transversions)
							line = next(infile)
							tstvs=line.split(",")
							#print(tstvs)
						for i in range(len(sampleName)-2):
							if(sampleName[i+1] != ""):
								tstvrow = TSTVRow.objects.create(filename=name)
								tstvrow.sample=sampleName[i+1]
								tstvrow.transitions=transitions[i+1]
								tstvrow.transversions=transversions[i+1]
								tstvrow.tstv=tstvs[i+1]
								tstvrow.tablename="TSTVALLVARIANTS"
								tstvrow.save()
							
							#annotaion = Annotation.objects.create()
							#annotation.postion=tstvrow
					if(re.search(r'# Ts/Tv : Known',line)):
						line = next(infile)
						line = next(infile)
						if(re.search(r'Sample',line)):
							#line = next(infile)
							sampleName = line.split(",")
							#print(sampleName)
							line = next(infile)
							transitions = line.split(",")
							#print(transitions)
							line = next(infile)
							transversions = line.split(",")
							#print(transversions)
							line = next(infile)
							tstvs=line.split(",")
							#print(tstvs)
						for i in range(len(sampleName)-2):
							if(sampleName[i+1] != ""):
								tstvrow = TSTVKnownRow.objects.create(filename=name)
								tstvrow.sample=sampleName[i+1]
								tstvrow.transitions=transitions[i+1]
								tstvrow.transversions=transversions[i+1]
								tstvrow.tstv=tstvs[i+1]
								tstvrow.tablename="TSTVKNOWNVARIANTS"
								tstvrow.save()
					if(re.search(r'# Hom/Het',line)):
						line = next(infile)
						line = next(infile)
						if(re.search(r'Sample_names',line)):
							sampleName = line.split(",")
							line = next(infile)
							reference = line.split(",")
							line = next(infile)
							het = line.split(",")
							line = next(infile)
							hom = line.split(",")
							line = next(infile)
							missing = line.split(",")
						for i in range(len(sampleName)-2):
							if(sampleName[i+1] != ""):
								homhetrow = HomHet.objects.create(filename=name)
								homhetrow.sample=sampleName[i+1]
								homhetrow.reference=reference[i+1]
								homhetrow.hom=hom[i+1]
								homhetrow.het=het[i+1]
								homhetrow.missing=missing[i+1]
								homhetrow.tablename="HomHetTable"
								homhetrow.save()
				msg = "Uploaded successfully !!!!"			
				infile.close()
			if name.endswith('.vcf'):
				vcf_reader = vcf.VCFReader(open(os.path.join(settings.MEDIA_ROOT,'vcffiles',name),'r'))
				experimentrow = Experiment.objects.create()
				experimentrow.experiment_name=request.POST['experiment_name']
				experimentrow.genome_build=request.POST['genome_build']
				experimentrow.save()
				for record in vcf_reader:
					positionrow = Position.objects.create(experiment=experimentrow)
					positionrow.pos = record.POS
					positionrow.chromosome = record.CHROM
					positionrow.rsid = record.ID
					positionrow.ref_nucl = record.REF
					positionrow.alt_nucl = record.ALT
					positionrow.quality = record.QUAL
					positionrow.filter = record.FILTER
					positionrow.allele_count = record.INFO['AC']
					positionrow.allele_frequency = record.INFO['AF']
					positionrow.total_no_of_alleles = record.INFO['AN']
					positionrow.experimentId = experimentrow.experiment_name
					positionrow.save()
					all_annotations = record.INFO['ANN']
					for i in range(len(all_annotations)):
						annotationrow = Annotation.objects.create(position=positionrow)
						annotationrow.positionId = positionrow.pos
						annotationfields = all_annotations[i].split('|')
						annotationrow.allele = annotationfields[0]
						annotationrow.annotation = annotationfields[1]
						annotationrow.annotation_impact = annotationfields[2]
						annotationrow.gene_name = annotationfields[3]
						annotationrow.gene_id = annotationfields[4]
						annotationrow.feature_type = annotationfields[5]
						annotationrow.feature_id = annotationfields[6]
						annotationrow.transcript_biotype = annotationfields[7]
						annotationrow.rank = annotationfields[8]
						annotationrow.hgvs_c = annotationfields[9]
						annotationrow.hgvs_p = annotationfields[10]
						annotationrow.cdna_pos_length = annotationfields[11]
						annotationrow.cds_pos_length = annotationfields[12]
						annotationrow.aa_pos_length = annotationfields[13]
						annotationrow.distance = annotationfields[14]
						annotationrow.warnings = annotationfields[15]
						annotationrow.experimentId = experimentrow.experiment_name
						annotationrow.save()
					all_samples = (vcf_reader.samples)	
					for i in range(len(all_samples)):
						samplerow = Sample.objects.create(position=positionrow,experiment=experimentrow)
						samplerow.experimentId = experimentrow.experiment_name
						samplerow.positionId = positionrow.pos
						samplerow.sampleId = all_samples[i]
						call = record.genotype(all_samples[i])
						sample_data = call.data
						samplerow.genotype = sample_data[0]
						samplerow.allellic_depth = sample_data[1]
						samplerow.read_depth = sample_data[2]
						samplerow.genotype_quality = sample_data[3]
						samplerow.pl = sample_data[4]
						samplerow.save()

			msg = "Uploaded successfully !!!!"			
			#vcf_reader.close()
			
			#Upload.objects.all().delete()
		params['msg'] = msg
		return render(request,'home.html', params)
	else:
		img=UploadForm()
	images=Upload.objects.all()
	return render(request,'home.html',{'form':img,'images':images})
	
	
def listpositions(request):
	positionlist = Position.objects
	#annotationlist = Annotation.objects
	#samplelist = Sample.objects
	positions = []
	#annotations = []
	#samples = []
	for position in positionlist.all():
		params = {}
		eachrow=[]
		eachrow.append(position.pos)
		eachrow.append(position.chromosome)
		eachrow.append(position.rsid)
		eachrow.append(position.ref_nucl)
		eachrow.append(position.alt_nucl)
		eachrow.append(position.quality)
		eachrow.append(position.filter)
		eachrow.append(position.allele_count)
		eachrow.append(position.allele_frequency)
		eachrow.append(position.total_no_of_alleles)
		positions.append(eachrow)
	'''for annotation in annotationlist.all():
		params = {}
		eachrow=[]
		eachrow.append(annotation.allele)
		eachrow.append(annotation.annotation)
		eachrow.append(annotation.annotation_impact)
		eachrow.append(annotation.gene_name)
		eachrow.append(annotation.gene_id)
		eachrow.append(annotation.feature_type)
		eachrow.append(annotation.feature_id)
		eachrow.append(annotation.transcript_biotype)
		eachrow.append(annotation.rank)
		eachrow.append(annotation.hgvs_c)
		eachrow.append(annotation.hgvs_p)
		eachrow.append(annotation.cdna_pos_length)
		eachrow.append(annotation.cds_pos_length)
		eachrow.append(annotation.aa_pos_length)
		eachrow.append(annotation.distance)
		eachrow.append(annotation.warnings)
		annotations.append(eachrow)
	for sample in samplelist.all():
		params = {}
		eachrow=[]
		eachrow.append(sample.positionId)
		eachrow.append(sample.sampleId)
		eachrow.append(sample.genotype)
		eachrow.append(sample.allellic_depth)
		eachrow.append(sample.read_depth)
		eachrow.append(sample.genotype_quality)
		eachrow.append(sample.pl)
		samples.append(eachrow)
		'''
	params['positions'] = positions
	#params['annotations'] = annotations
	#params['samples'] = samples
	return render(request, 'link.html', params)
	
def listtsttable(request):
	annotationlist = TSTVRow.objects
	results=[]
	knownvariants=[]
	HomHetRatio=[]
	
	for annotation in annotationlist.all():
		params = {}
		eachrow=[]
		eachrow.append(annotation.sample)
		eachrow.append(annotation.transitions)
		eachrow.append(annotation.transversions)
		eachrow.append(annotation.tstv)
		results.append(eachrow)
	knownlist=TSTVKnownRow.objects
	for annotation in knownlist.all():
		
		eachrow=[]
		eachrow.append(annotation.sample)
		eachrow.append(annotation.transitions)
		eachrow.append(annotation.transversions)
		eachrow.append(annotation.tstv)
		knownvariants.append(eachrow)
	HomHetlist=HomHet.objects
	for annotation in HomHetlist.all():
		
		eachrow=[]
		eachrow.append(annotation.sample)
		eachrow.append(annotation.reference)
		eachrow.append(annotation.hom)
		eachrow.append(annotation.het)
		eachrow.append(annotation.missing)
		HomHetRatio.append(eachrow)
	params['results'] = results
	params['knownvariants']=knownvariants
	params['HomHetRatio']=HomHetRatio
	return render(request, 'list.html', params)
	
	
def viewannotations(request):
	params={}
	annotations = []
	if 'positionId' in request.GET and request.GET['positionId']:
		position = request.GET['positionId']
		annotationlist = Annotation.objects.filter(positionId=position)
		for annotation in annotationlist.all():
			eachrow=[]
			eachrow.append(annotation.allele)
			eachrow.append(annotation.annotation)
			eachrow.append(annotation.annotation_impact)
			eachrow.append(annotation.gene_name)
			eachrow.append(annotation.gene_id)
			eachrow.append(annotation.feature_type)
			eachrow.append(annotation.feature_id)
			eachrow.append(annotation.transcript_biotype)
			eachrow.append(annotation.rank)
			eachrow.append(annotation.hgvs_c)
			eachrow.append(annotation.hgvs_p)
			eachrow.append(annotation.cdna_pos_length)
			eachrow.append(annotation.cds_pos_length)
			eachrow.append(annotation.aa_pos_length)
			eachrow.append(annotation.distance)
			eachrow.append(annotation.warnings)
			annotations.append(eachrow)
		params['annotations'] = annotations
	return render(request, 'viewannotations.html', params)
	
def viewsamples(request):
	params={}
	samples = []
	if 'positionId' in request.GET and request.GET['positionId']:
		position = request.GET['positionId']
		samplelist = Sample.objects.filter(positionId=position)
		for sample in samplelist.all():
			eachrow=[]
			eachrow.append(sample.positionId)
			eachrow.append(sample.sampleId)
			eachrow.append(sample.genotype)
			eachrow.append(sample.allellic_depth)
			eachrow.append(sample.read_depth)
			eachrow.append(sample.genotype_quality)
			eachrow.append(sample.pl)
			samples.append(eachrow)
		params['samples'] = samples
	return render(request, 'viewsamples.html', params)

def viewannotationdata(request):
	params={}
	annotations = []
	if 'positionId' in request.GET and request.GET['positionId']:
		position = request.GET['positionId']
		annotationlist = Annotation.objects.filter(annotation_impact=position)
		for annotation in annotationlist.all():
			eachrow=[]
			eachrow.append(annotation.allele)
			eachrow.append(annotation.annotation)
			eachrow.append(annotation.annotation_impact)
			eachrow.append(annotation.gene_name)
			eachrow.append(annotation.gene_id)
			eachrow.append(annotation.feature_type)
			eachrow.append(annotation.feature_id)
			eachrow.append(annotation.transcript_biotype)
			eachrow.append(annotation.rank)
			eachrow.append(annotation.hgvs_c)
			eachrow.append(annotation.hgvs_p)
			eachrow.append(annotation.cdna_pos_length)
			eachrow.append(annotation.cds_pos_length)
			eachrow.append(annotation.aa_pos_length)
			eachrow.append(annotation.distance)
			eachrow.append(annotation.warnings)
			annotations.append(eachrow)
		params['annotations'] = annotations
	return render(request, 'viewannotations.html', params)
	
def viewsampledata(request):
	params={}
	samples = []
	if 'positionId' in request.GET and request.GET['positionId']:
		position = request.GET['positionId']
		samplelist = Sample.objects.filter(sampleId=position)
		for sample in samplelist.all():
			eachrow=[]
			eachrow.append(sample.positionId)
			eachrow.append(sample.sampleId)
			eachrow.append(sample.genotype)
			eachrow.append(sample.allellic_depth)
			eachrow.append(sample.read_depth)
			eachrow.append(sample.genotype_quality)
			eachrow.append(sample.pl)
			samples.append(eachrow)
		params['samples'] = samples
	return render(request, 'viewsamples.html', params)


		
def search(request):	
  return render(request, 'search.html')	
 
def posSearch(request):
	return render(request, 'posSearch.html')
	
def possearchresult(request):
	params = {}
	if 'position' in request.POST and request.POST['position']:
		print("I am in if")
		searchdata = request.POST['position']
		positionlist = Position.objects.filter(pos=searchdata)
		annotationlist = Annotation.objects.filter(positionId=searchdata)
		samplelist = Sample.objects.filter(positionId=searchdata)
		positions = []
		annotations = []
		samples = []
		for po in positionlist.all():
			eachrow=[]
			eachrow.append(po.pos)
			eachrow.append(po.chromosome)
			eachrow.append(po.rsid)
			eachrow.append(po.ref_nucl)
			eachrow.append(po.alt_nucl)
			eachrow.append(po.quality)
			eachrow.append(po.filter)
			eachrow.append(po.allele_count)
			eachrow.append(po.allele_frequency)
			eachrow.append(po.total_no_of_alleles)
			positions.append(eachrow)
		for annotation in annotationlist.all():
			eachrow=[]
			eachrow.append(annotation.allele)
			eachrow.append(annotation.annotation)
			eachrow.append(annotation.annotation_impact)
			eachrow.append(annotation.gene_name)
			eachrow.append(annotation.gene_id)
			eachrow.append(annotation.feature_type)
			eachrow.append(annotation.feature_id)
			eachrow.append(annotation.transcript_biotype)
			eachrow.append(annotation.rank)
			eachrow.append(annotation.hgvs_c)
			eachrow.append(annotation.hgvs_p)
			eachrow.append(annotation.cdna_pos_length)
			eachrow.append(annotation.cds_pos_length)
			eachrow.append(annotation.aa_pos_length)
			eachrow.append(annotation.distance)
			eachrow.append(annotation.warnings)
			annotations.append(eachrow)
		for sample in samplelist.all():
			eachrow=[]
			eachrow.append(sample.positionId)
			eachrow.append(sample.sampleId)
			eachrow.append(sample.genotype)
			eachrow.append(sample.allellic_depth)
			eachrow.append(sample.read_depth)
			eachrow.append(sample.genotype_quality)
			eachrow.append(sample.pl)
			samples.append(eachrow)
		params['positions'] = positions
		params['annotations'] = annotations
		params['samples'] = samples
	return render(request, 'link.html', params)
	
def pseSearch(request):
	experiment = Experiment.objects.all() 
	chromo  = Position.objects.order_by().values('chromosome').distinct()
	position  = Position.objects.all() 
	sample = Sample.objects.all()
	annotation = Annotation.objects.order_by().values('annotation_impact').distinct() 
	return render_to_response ('integratedSearch.html', {'experiments':experiment,'chromosomes':chromo,'positions':position,'samples':sample,'annotations':annotation}, context_instance =  RequestContext(request),)

	
def psesearchresult(request):
	if request.method == 'POST':
		params={}
		experiment = request.POST['experiment']
		chromo = request.POST['chromo']
		position1 = request.POST['position1']
		position2 = request.POST['position2']
		sample = request.POST['sample']
		annotation = request.POST['annotation']
		positions = []
		cursor = connection.cursor()
		if chromo=="-":
			chromo="%"
		if position1=="-":
			position1="%"
		if sample=="-":
			sample="%"
		if annotation=="-":
			annotation="%"
		if experiment=="-":
			experiment="%"
		#query = "select * From anveshikaapp_position inner join anveshikaapp_sample on (anveshikaapp_position.pos=anveshikaapp_sample.positionId)where  anveshikaapp_position.chromosome LIKE \'" + chromo+ "\' and anveshikaapp_position.pos LIKE '" + position1 +"' and anveshikaapp_sample.sampleid LIKE \'"+sample+"\'"
		if position2=="-":
			query = "select * From anveshikaapp_position inner join anveshikaapp_sample on (anveshikaapp_position.pos=anveshikaapp_sample.positionId) inner join anveshikaapp_annotation on (anveshikaapp_position.pos=anveshikaapp_annotation.positionId)where  anveshikaapp_position.experimentId LIKE \'" + experiment+ "\' and anveshikaapp_position.chromosome LIKE \'" + chromo+ "\' and anveshikaapp_position.pos LIKE \'" + position1 +"\' and anveshikaapp_sample.sampleid LIKE \'"+sample+"\' and anveshikaapp_annotation.annotation_impact LIKE \'"+annotation+"\'"
		else:
			query = "select * From anveshikaapp_position inner join anveshikaapp_sample on (anveshikaapp_position.pos=anveshikaapp_sample.positionId) inner join anveshikaapp_annotation on (anveshikaapp_position.pos=anveshikaapp_annotation.positionId)where  anveshikaapp_position.experimentId LIKE \'" + experiment+ "\' and anveshikaapp_position.chromosome LIKE \'" + chromo+ "\' and anveshikaapp_position.pos  BETWEEN \'" + position1 +"\' AND \'"+position2+"\' and anveshikaapp_sample.sampleid LIKE \'"+sample+"\' and anveshikaapp_annotation.annotation_impact LIKE \'"+annotation+"\'"
		print(query)
		cursor.execute(query)
		
		
		#solution = cursor.fetchall()
		for po in cursor.fetchall():
			eachrow=[] 
			eachrow.append(po[12])
			eachrow.append(po[2])
			eachrow.append(po[3])
			eachrow.append(po[4])
			eachrow.append(po[5])
			eachrow.append(po[6])
			eachrow.append(po[7])
			eachrow.append(po[9])
			eachrow.append(po[10])
			eachrow.append(po[11])
			eachrow.append(po[18])
			eachrow.append(po[29])
			positions.append(eachrow)
		params['positions'] = positions
		'''annotationlist = Annotation.objects.filter(positionId=possearch)
		positionlist = Position.objects.filter(pos=possearch)
		#If only position is provided
		if(samplesearch==''):
			if(experimentsearch!=''):
				samplelist = Sample.objects.filter(positionId=possearch,experimentId=experimentsearch)
			else:
				samplelist = Sample.objects.filter(positionId=possearch)
		#If only sample is provided
		elif(possearch==''):
			if(experimentsearch!=''):
				samplelist = Sample.objects.filter(sampleId=samplesearch,experimentId=experimentsearch)
			else:
				samplelist = Sample.objects.filter(sampleId=samplesearch)
		#If both position and sample are provided
		elif(samplesearch!='' and  possearch!=''):
			if(experimentsearch!=''):
				samplelist = Sample.objects.filter(sampleId=samplesearch,positionId=possearch,experimentId=experimentsearch)
			else:
				samplelist = Sample.objects.filter(sampleId=samplesearch,positionId=possearch)
		#If only experiment is provided
		if(samplesearch=='' and  possearch=='' and experimentsearch!=''):
			samplelist = Sample.objects.filter(experimentId=experimentsearch)
		

		
		params = {}
		positions=[]
		annotations=[]
		samples=[]
		all_annotations=[]
		positionsinsamples=[]
		annotationsinallsamples=[]
		for sample in samplelist.all():
			if((sample.genotype == '1/1' or sample.genotype == '0/1' )and (sample.experiment.experiment_name==experimentsearch or experimentsearch=='' ) ):
				eachrow=[]
				eachrow.append(sample.experiment.experiment_name)
				eachrow.append(sample.positionId)
				eachrow.append(sample.sampleId)
				eachrow.append(sample.genotype)
				eachrow.append(sample.allellic_depth)
				eachrow.append(sample.read_depth)
				eachrow.append(sample.genotype_quality)
				eachrow.append(sample.pl)
				samples.append(eachrow)
				if 	sample.positionId not in positionsinsamples: 	
					annotationlist = Annotation.objects.filter(positionId=sample.positionId)
					annotationsinallsamples.extend(annotationlist)
					positionsinsamples.append(sample.positionId)
				for annotation in annotationsinallsamples:
					eachrow=[]
					eachrow.append(annotation.allele)
					eachrow.append(annotation.annotation)
					eachrow.append(annotation.annotation_impact)
					eachrow.append(annotation.gene_name)
					eachrow.append(annotation.gene_id)
					eachrow.append(annotation.feature_type)
					eachrow.append(annotation.feature_id)
					eachrow.append(annotation.transcript_biotype)
					eachrow.append(annotation.rank)
					eachrow.append(annotation.hgvs_c)
					eachrow.append(annotation.hgvs_p)
					eachrow.append(annotation.cdna_pos_length)
					eachrow.append(annotation.cds_pos_length)
					eachrow.append(annotation.aa_pos_length)
					eachrow.append(annotation.distance)
					eachrow.append(annotation.warnings)
					annotations.append(eachrow)
		params['annotations'] = annotations'''
	#return render(request, 'login.html', params)
	return render(request, 'searchresults.html', params)
		
def searchresult(request):
	params = {}
	if 'sample' in request.POST and request.POST['sample']:
		searchdata = request.POST['sample']
		tstvrowlist = TSTVRow.objects.filter(sample=searchdata)
		tstvknownrowlist = TSTVKnownRow.objects.filter(sample=searchdata)
		homhetrowlist = HomHet.objects.filter(sample=searchdata)
		results=[]
		knowvariants=[]
		homhetratio=[]
		for tstv in tstvrowlist.all():
			eachrow=[]
			eachrow.append(tstv.sample)
			eachrow.append(tstv.transitions)
			eachrow.append(tstv.transversions)
			eachrow.append(tstv.tstv)
			#eachrow.append(tstv.tablename)
			#eachrow.append(tstv.filename)
			results.append(eachrow)
		for tstvknown in tstvknownrowlist.all():
			eachrow=[]
			eachrow.append(tstvknown.sample)
			eachrow.append(tstvknown.transitions)
			eachrow.append(tstvknown.transversions)
			eachrow.append(tstvknown.tstv)
			#eachrow.append(tstvknown.tablename)
			#eachrow.append(tstvknown.filename)
			knowvariants.append(eachrow)
		for homhet in homhetrowlist.all():
			eachrow=[]
			#print("hello")
			#print(homhet.sample)
			eachrow.append(homhet.sample)
			eachrow.append(homhet.reference)
			eachrow.append(homhet.hom)
			eachrow.append(homhet.het)
			eachrow.append(homhet.missing)
			#eachrow.append(homhet.tablename)
			#eachrow.append(homhet.filename)
			homhetratio.append(eachrow)
		
		params['results'] = results
		params['knownvariants'] = knowvariants
		params['HomHetRatio'] = homhetratio
	return render(request, 'list.html', params)	

