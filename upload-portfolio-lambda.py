import json

import boto3
from botocore.client import Config
import StringIO
import zipfile

def lambda_handler(event, context):
    # TODO implement
    
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:789094691283:deployPortfolioTopic')
    
    try:
    
        job = event.get("CodePipeline.job")
        
        location = {
            "bucketName": 'portfoliobuild.ciarancod.es',
            "objectKey": 'portfoliobuild.zip'
        }
        
        
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]
        
        print "Building portfolio from" + str(location)
        
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
    
        portfolio_bucket = s3.Bucket('ciarancod.es')
        build_bucket = s3.Bucket(location["bucketName"])
    
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)
    
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
            
    except:
        topic.publish(Subject="Portfolio Deploy Failed",
          Message="Portfolio was not deployed successfully.")
        raise


    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
