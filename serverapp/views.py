from django.shortcuts import render, redirect
import os
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings
from serverapp.forms import AzureForm
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import boto3
from dotenv import load_dotenv

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth

from django.shortcuts import render
import os
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings
from serverapp.forms import AzureForm, AzureForm2
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import boto3
import ast
from cryptography.fernet import Fernet
from serverapp.models import Document
import glob
from django.http import StreamingHttpResponse
import shutil
from botocore.exceptions import ClientError
import botocore

def call_key():
    return open("static/pass.key", "rb").read()
key = call_key()
a = Fernet(key)

#index
def index(request):
    return render(request, 'login.html')

#login views
def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username, password = password)


        if user is not None:
            if user.is_active and user.is_staff:
                login(request,user)
                return HttpResponseRedirect(reverse('form_data'))
            else:
                return HttpResponse('Account not Active')
        else:
            messages.error(request, 'Invalid Login Credentials!')
            return redirect('index')

    else:
        return HttpResponseRedirect(reverse('index'))

#logout views
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Successfully logged off!')
    return HttpResponseRedirect(reverse('index'))

# Create your views here.

blob_names = {}
@login_required
def file_select(request):
    MY_CONNECTION_STRING = request.session['con_str']
    MY_IMAGE_CONTAINER = request.session['con_name']
    AWS_ACCESS_KEY_ID = request.session['key_id']
    AWS_ACCESS_KEY_SECRET = request.session['key_secret']
    BUCKET_NAME = request.session['bucket_name']
    SERVER = request.session['server']
    REGION_NAME = 'us-east-1'
    load_dotenv(verbose=True)

    files = glob.glob("downloads/*")
    for file in files:
        os.remove(file)

    try:
        def aws_session(region_name=REGION_NAME):
            return boto3.session.Session(aws_access_key_id=os.getenv(a.decrypt(AWS_ACCESS_KEY_ID.encode('utf-8')).decode('utf-8')),
                                    aws_secret_access_key=os.getenv(a.decrypt(AWS_ACCESS_KEY_SECRET.encode('utf-8')).decode('utf-8')),
                                    region_name=region_name)


        if SERVER == 'azure':
            my_blobs = BlobServiceClient.from_connection_string(a.decrypt(MY_CONNECTION_STRING.encode('utf-8')).decode('utf-8')).get_container_client(MY_IMAGE_CONTAINER).list_blobs()
            file_names = []
            for blob in my_blobs:
                file_names.append(blob.name)
                blob_names[blob.name] = blob
            request.session['file_names'] = file_names

        else:
            s3_resource = aws_session().resource('s3', aws_access_key_id=a.decrypt(AWS_ACCESS_KEY_ID.encode('utf-8')).decode('utf-8'),
                aws_secret_access_key= a.decrypt(AWS_ACCESS_KEY_SECRET.encode('utf-8')).decode('utf-8'))
            bucket = s3_resource.Bucket(BUCKET_NAME)
            file_names = []
            for bucket_content in bucket.objects.all():
                file_names.append(bucket_content.key)
            request.session['file_names'] = file_names

        file_names = request.session['file_names']
        return render(request, 'files.html', {'file_names': file_names})
    except Exception as E:
        messages.error(request, 'Invalid AWS/Azure Credentials!')
        return redirect('form_data')

# @login_required
def home(request):
    MY_CONNECTION_STRING = request.session['con_str']
    MY_IMAGE_CONTAINER = request.session['con_name']
    AWS_ACCESS_KEY_ID = request.session['key_id']
    AWS_ACCESS_KEY_SECRET = request.session['key_secret']
    BUCKET_NAME = request.session['bucket_name']
    SERVER = request.session['server']
    UP_DW = request.session['u_d']
    LOCAL_BLOB_PATH = "downloads"
    REGION_NAME = 'us-east-1'
    load_dotenv(verbose=True)

    files = glob.glob("downloads/*")
    for file in files:
        os.remove(file)
    try:
        def azure_upload_image(file_name):
            blob_service_client =  BlobServiceClient.from_connection_string(a.decrypt(MY_CONNECTION_STRING.encode('utf-8')).decode('utf-8'))
            blob_client = blob_service_client.get_blob_client(container=MY_IMAGE_CONTAINER, blob=file_name)
            ext = file_name.split('.')[-1]
            image_content_setting = ContentSettings(content_type=ext+'/'+ext)
            with open(file_name, "rb") as data:
                blob_client.upload_blob(data,overwrite=True,content_settings=image_content_setting)

        def save_blob(file_name,file_content):
            file = file_name.split("/")[1]
            download_file_path = os.path.join(LOCAL_BLOB_PATH, file)
            with open(download_file_path, "wb") as file:
                file.write(file_content)

        def aws_session(region_name=REGION_NAME):
            return boto3.session.Session(aws_access_key_id=os.getenv(a.decrypt(AWS_ACCESS_KEY_ID.encode('utf-8')).decode('utf-8')),
                                    aws_secret_access_key=os.getenv(a.decrypt(AWS_ACCESS_KEY_SECRET.encode('utf-8')).decode('utf-8')),
                                    region_name=region_name)

        def upload_file_to_bucket(bucket_name, file_path):
            s3_resource = aws_session().resource('s3', aws_access_key_id=a.decrypt(AWS_ACCESS_KEY_ID.encode('utf-8')).decode('utf-8'),
                aws_secret_access_key= a.decrypt(AWS_ACCESS_KEY_SECRET.encode('utf-8')).decode('utf-8'))
            file_dir, file_name = os.path.split(file_path)
            bucket = s3_resource.Bucket(bucket_name)
            bucket.upload_file(
            Filename=file_path,
            Key=file_name,
            ExtraArgs={'ACL': 'public-read'}
            )

        def download_file_from_bucket(bucket_name, s3_key, dst_path):
            s3_resource = aws_session().resource('s3', aws_access_key_id=a.decrypt(AWS_ACCESS_KEY_ID.encode('utf-8')).decode('utf-8'),
                aws_secret_access_key= a.decrypt(AWS_ACCESS_KEY_SECRET.encode('utf-8')).decode('utf-8'))
            bucket = s3_resource.Bucket(bucket_name)
            bucket.download_file(Key=s3_key, Filename=dst_path)

        if SERVER == 'azure' and UP_DW == 'upload':
            files = glob.glob('docs/*')
            for file in files:
                azure_upload_image(file)
        elif SERVER == 'azure' and UP_DW == 'download':
            if request.method=='POST':
                form = AzureForm2(request.POST)
                if form.is_valid():
                    files = form.cleaned_data['choices']
                    files_new = ast.literal_eval(files)
                    for file in files_new:
                        blob = blob_names[file[:-1]]
                        bytes = BlobServiceClient.from_connection_string(a.decrypt(MY_CONNECTION_STRING.encode('utf-8')).decode('utf-8')).get_container_client(MY_IMAGE_CONTAINER).get_blob_client(blob).download_blob().readall()
                        save_blob(file, bytes)

        elif SERVER == 'aws' and UP_DW == 'upload':
            files = glob.glob('docs/*')
            for file in files:
                upload_file_to_bucket(BUCKET_NAME, file)
        elif SERVER == 'aws' and UP_DW == 'download':
            if request.method=='POST':
                form = AzureForm2(request.POST)
                if form.is_valid():
                    files = form.cleaned_data['choices']
                    files_new = ast.literal_eval(files)
                    for file in files_new:
                        file_path = os.path.join(LOCAL_BLOB_PATH, file)
                        download_file_from_bucket(BUCKET_NAME, file[:-1], file_path[:-1])
        if UP_DW == "download":
            shutil.make_archive('files_archieve', 'zip', 'downloads')
            file = open('files_archieve.zip', 'rb')
            response = StreamingHttpResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['content-Disposition'] = 'attachment;filename="files_archieve.zip"'
            files = glob.glob('docs/*')
            for file in files:
                os.remove(file)
            return response
        else:
            for file in files:
                os.remove(file)
            return render(request, 'home.html')
    except Exception as E:
        messages.error(request, 'Invalid Login Credentials!')
        return redirect('form_data')

@login_required
def form_data(request):
    try:
        if request.method == 'POST':
            form = AzureForm(request.POST, request.FILES)
            files = request.FILES.getlist('document')
            if form.is_valid():
                for f in files:
                    file_ins = Document(document = f)
                    file_ins.save()
                server_name = form.cleaned_data['server']
                request.session['server'] = server_name
                con_name = request.POST.get('con_name')
                request.session['con_name'] = con_name
                con_str = request.POST.get('con_str')
                request.session['con_str'] = con_str
                key_id = request.POST.get('key_id')
                request.session['key_id'] = key_id
                key_secret = request.POST.get('key_secret')
                request.session['key_secret'] = key_secret
                bucket_name = request.POST.get('bucket_name')
                request.session['bucket_name'] = bucket_name
                up_dw = form.cleaned_data['u_d']
                request.session['u_d'] = up_dw
                if up_dw == "upload":
                    return HttpResponseRedirect(reverse('home'))
                else:
                    return HttpResponseRedirect(reverse('files'))

        else:
            form = AzureForm()
        return render(request, 'form.html', {"form": form})
    except Exception as E:
        messages.error(request, 'Invalid Login Credentials!')
        return redirect('form_data')
