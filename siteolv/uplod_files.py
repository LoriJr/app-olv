import boto3
BUCKET = 'ad-petroni-avulsos'

lista = ['foto_print.jpg', 'gundam.jpg']
s3 = boto3.client('s3')

for i in lista:
    s3.upload_file(i, BUCKET, i, ExtraArgs={'ContentType': 'image/jpeg'})

