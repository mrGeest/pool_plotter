# Store the location of the current file so that we can specify a relative path that will always work
# (A crontab runs the script from ~, for example)
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
data_folder = os.path.join(__location__, '../pool_logger_data/')

# This is where the files from the raspberry pi come in:
upload_folder = '/upload_folder/'

