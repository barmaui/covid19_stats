from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
def launch_pipeline(request):
    credentials = GoogleCredentials.get_application_default()
    service = build('dataflow', 'v1b3', credentials=credentials)
    # Update the below four variables to reflect your requirements
    JOBNAME = "Daily Update COVID19 data"
    PROJECT = "covid19stats-273220"
    BUCKET = "covid19_pipeline_code"
    TEMPLATE = "daily_update_template"
    GCSPATH = "gs://{bucket}/templates/{template}".format(bucket=BUCKET, template=TEMPLATE)
    BODY = {
        "jobName": "{jobname}".format(jobname=JOBNAME),
        "parameters": {
            "region": "us-central1"
        },
        "environment": {
            "tempLocation": "gs://{bucket}/temp".format(bucket=BUCKET),
        }
    }
    request = service.projects().templates().launch(projectId=PROJECT, gcsPath=GCSPATH, body=BODY)
    response = request.execute()
    print(response)