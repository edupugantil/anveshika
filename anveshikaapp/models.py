from django.db import models
from django.contrib.auth.models import User,Group
from django.forms import ModelForm
from django import forms

# Create your models here.

class Upload(models.Model):
	img = models.FileField("VCFFile", upload_to="vcffiles/")    
	upload_date=models.DateTimeField(auto_now_add =True)
	experiment_name=models.CharField(max_length=500)
	genome_build= models.CharField(max_length=500)

# FileUpload form class.
class UploadForm(ModelForm):
	class Meta:
		model = Upload
		fields = '__all__'		
		
class Experiment(models.Model):
	experiment_name = models.CharField(max_length=500)
	genome_build = models.CharField(max_length=500)
	
class Position(models.Model):
	experiment = models.ForeignKey(Experiment)
	pos = models.CharField(max_length=50,null=True,blank=True)
	chromosome = models.CharField(max_length=50,null=True,blank=True)
	rsid = models.CharField(max_length=50,null=True,blank=True)
	ref_nucl = models.CharField(max_length=50,null=True,blank=True)
	alt_nucl = models.CharField(max_length=50,null=True,blank=True)
	quality =  models.CharField(max_length=50,null=True,blank=True)
	filter = models.CharField(max_length=50,null=True,blank=True)
	allele_count = models.CharField(max_length=50,null=True,blank=True)
	allele_frequency = models.CharField(max_length=50,null=True,blank=True)
	total_no_of_alleles = models.CharField(max_length=50,null=True,blank=True)
	experimentId = models.CharField(max_length=50,null=True,blank=True)

class Annotation(models.Model):
	position = models.ForeignKey(Position)
	positionId = models.CharField(max_length=50,null=True,blank=True)
	allele = models.CharField(max_length=50,null=True,blank=True)
	annotation =  models.CharField(max_length=50,null=True,blank=True)
	annotation_impact = models.CharField(max_length=50,null=True,blank=True)
	gene_name = models.CharField(max_length=50,null=True,blank=True)
	gene_id = models.CharField(max_length=50,null=True,blank=True)
	feature_type = models.CharField(max_length=50,null=True,blank=True)
	feature_id = models.CharField(max_length=50,null=True,blank=True)
	transcript_biotype = models.CharField(max_length=50,null=True,blank=True)
	rank = models.CharField(max_length=50,null=True,blank=True)
	hgvs_c = models.CharField(max_length=50,null=True,blank=True)
	hgvs_p = models.CharField(max_length=50,null=True,blank=True)
	cdna_pos_length = models.CharField(max_length=50,null=True,blank=True)
	cds_pos_length = models.CharField(max_length=50,null=True,blank=True)
	aa_pos_length = models.CharField(max_length=50,null=True,blank=True)
	distance = models.CharField(max_length=50,null=True,blank=True)
	warnings = models.TextField(null=True,blank=True)
	experimentId = models.CharField(max_length=50,null=True,blank=True)

class Sample(models.Model):
	position = models.ForeignKey(Position)
	experiment = models.ForeignKey(Experiment)
	experimentId = models.CharField(max_length=50,null=True,blank=True)
	positionId = models.CharField(max_length=50,null=True,blank=True)
	sampleId = models.CharField(max_length=100,blank=True,null=True)
	genotype = models.CharField(max_length=100,blank=True,null=True)
	allellic_depth = models.CharField(max_length=50,null=True,blank=True)
	read_depth = models.CharField(max_length=50,null=True,blank=True)
	genotype_quality = models.CharField(max_length=50,null=True,blank=True)
	pl = models.CharField(max_length=50,null=True,blank=True)

class TSTVRow(models.Model):
	sample=models.CharField(max_length=500)
	transitions=models.CharField(max_length=500)
	transversions=models.CharField(max_length=500)
	tstv=models.CharField(max_length=500)
	tablename=models.CharField(max_length=500)
	filename=models.CharField(max_length=500)
	

	
class TSTVKnownRow(models.Model):
	sample=models.CharField(max_length=500)
	transitions=models.CharField(max_length=500)
	transversions=models.CharField(max_length=500)
	tstv=models.CharField(max_length=500)
	tablename=models.CharField(max_length=500)
	filename=models.CharField(max_length=500)
	
class HomHet(models.Model):
	sample=models.CharField(max_length=500)
	reference=models.CharField(max_length=500)
	hom=models.CharField(max_length=500)
	het=models.CharField(max_length=500)
	missing=models.CharField(max_length=500)
	tablename=models.CharField(max_length=500)
	filename=models.CharField(max_length=500)
	

	
	

	
	