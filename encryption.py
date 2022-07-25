from cryptography.fernet import Fernet

def call_key():
    return open("static/pass.key", "rb").read()

key = call_key()
a = Fernet(key)

print("Enter connection string for azure")
con_str = input().encode()
coded_con_str = a.encrypt(con_str)
print("Encoded connection String is: ", coded_con_str)
with open("azure_con_str.txt", "wb") as cred_file1:
    cred_file1.write(coded_con_str)

print("Enter AWS Access key ID")
aws_key_id = input().encode()
coded_aws_id = a.encrypt(aws_key_id)
print("Encoded AWS Key ID is: ", coded_aws_id)
print("Enter AWS key")
aws_key = input().encode()
coded_aws_key = a.encrypt(aws_key)
print("Encoded AWS Key is: ", coded_aws_key)
with open("aws_id.txt", "wb") as cred_file2:
    cred_file2.write(coded_aws_id)
with open("aws_key.txt", "wb") as cred_file3:
    cred_file3.write(coded_aws_key)