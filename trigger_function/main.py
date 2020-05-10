def launch_pipeline(data, context):
    from googleapiclient.discovery import build
    from oauth2client.client import GoogleCredentials
    from datetime import datetime, timedelta
    credentials = GoogleCredentials.get_application_default()
    yesterday = datetime.today() - timedelta(days=1)
    date_y = yesterday.strftime('%Y-%m-%d')
    service = build('dataflow', 'v1b3', credentials=credentials)
    # Update the below four variables to reflect your requirements
    JOBNAME = "Daily Update COVID19 data"
    PROJECT = "covid19stats-273220"
    BUCKET = "covid19_pipeline_code"
    TEMPLATE = "daily_update_template"
    GCSPATH = "gs://{bucket}/template/{template}".format(bucket=BUCKET, template=TEMPLATE)
    BODY = {
        "jobName": "{jobname}".format(jobname=JOBNAME),
        "parameters": {
            "region": "us-central1",
            "input_date": f'{date_y}'
        },
        "environment": {
            "tempLocation": "gs://{bucket}/temp".format(bucket=BUCKET),
        }
    }
    request = service.projects().templates().launch(projectId=PROJECT, gcsPath=GCSPATH, body=BODY)
    response = request.execute()
    print(response)