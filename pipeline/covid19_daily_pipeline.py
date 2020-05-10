import apache_beam as beam

from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import StandardOptions
import logging

class UserOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument('--input_date', dest='input_date', type='string', default='2020-05-08')

options = PipelineOptions()
user_options = options.view_as(UserOptions)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.debug(user_options.input_date.get())
google_cloud_options = options.view_as(GoogleCloudOptions)
google_cloud_options.project = "covid19stats-273220"
google_cloud_options.job_name = "daily-update-pipeline"
google_cloud_options.staging_location = "gs://covid19_stats/staging"
google_cloud_options.temp_location = "gs://covid19_stats/staging"
#options.view_as(StandardOptions).runner = "DirectRunner"  # use this for debugging
options.view_as(StandardOptions).runner = "DataFlowRunner"


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
    logging.debug(user_options)
    input_file = f'gs://covid19_stats/daily_stats_{user_options.input_date.get()}.csv'

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
                 project='covid19stats-273220',
                 schema='country:STRING,date:DATE,total_cases:INT64,new_cases:INT64,'
                 'total_deaths:INT64,new_deaths:INT64,active_cases:INT64',
                 # Creates the table in BigQuery if it does not yet exist.
                 create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                 # Deletes all data in the BigQuery table before writing.
                 write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)))

    result = p.run()
    result.wait_until_finish()


if __name__ == "__main__":
    run()
