# Cloud Agnostic Django Web app for files upload and download

This web application can be used to upload/download files between on prem(pc) and cloud service providers.  Currently this supports only AWS and Azure.
It has been build using django framework.

How to run the app:
1. Browse to the root directory and install dependencies using "pip install requirements.txt"
2. Run the app using the command "python manage.py runserver"
3. Access the app at the localhost

Note : The AWS or Azure credentials needs to encrypted using the provided key. The credentials will then be decrypted at server side. This has been done to implement client side encryption. 

For authentication, create your own user(from superuser)
