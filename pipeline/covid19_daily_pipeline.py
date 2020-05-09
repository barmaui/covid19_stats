import apache_beam as beam

from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import StandardOptions
from datetime import datetime, timedelta
options = PipelineOptions()
google_cloud_options = options.view_as(GoogleCloudOptions)
google_cloud_options.project = "covid19stats-273220"
google_cloud_options.job_name = "daily-update-pipeline"
google_cloud_options.staging_location = "gs://covid19_stats/staging"
google_cloud_options.temp_location = "gs://covid19_stats/staging"
#options.view_as(StandardOptions).runner = "DirectRunner"  # use this for debugging
options.view_as(StandardOptions).runner = "DataFlowRunner"

yesterday = datetime.today() - timedelta(days=1)
date_y = yesterday.strftime('%Y-%m-%d')
input_file = f'gs://covid19_stats/daily_stats_{date_y}.csv'


class CSVParser:
    """A helper class which contains the logic to translate the file into
    a format BigQuery will accept."""
    def parse_method(self, string_input):
        """This method translates a single line of comma separated values to a
        dictionary which can be loaded into BigQuery.
        Args:
            string_input: A comma separated list of values in the form of
                state_abbreviation,gender,year,name,count_of_babies,dataset_created_date
                Example string_input: USA,2020/03/01,1923,23,654,35,1200
        Returns:
            {
                'country': 'USA',
                'date': '2020/03/01',
                'total_cases': 1923,
                'new_cases': 23
                'total_deaths': 654
                'new_deaths': 35
            }
         """
        # Strip out carriage return, newline and quote characters.
        values = string_input.replace('\n', '').split(',')
        row = dict(zip(('country', 'date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths', 'active_cases'), values))
        print(row)
        return row


def run():
    """The main function which creates the pipeline and runs it."""

    csv_parser = CSVParser()

    p = beam.Pipeline(options=options)
    (p
    | 'Read from a File' >> beam.io.ReadFromText(input_file)
    | 'String To BigQuery Row' >> beam.Map(lambda s: csv_parser.parse_method(s))
    | 'Write to BigQuery' >> beam.io.Write(
             beam.io.WriteToBigQuery(
                 # The table name is a required argument for the BigQuery sink.
                 # In this case we use the value passed in from the command line.
                 'daily_stats',
                 dataset='covid19_stats',
                 project='covid19stats',
                 schema='country:STRING,date:DATE,total_cases:INT,new_cases:INT,'
                 'total_deaths:INT,new_deaths:INT,active_cases:INT',
                 # Creates the table in BigQuery if it does not yet exist.
                 create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                 # Deletes all data in the BigQuery table before writing.
                 write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)))

    result = p.run()
    result.wait_until_finish()


if __name__ == "__main__":
    run()
