# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

'''
Classes:
    RCMED - A class for retrieving data from Regional Climate Model Evalutaion Database (JPL).
    More information about the RCMED Query Specification can be found below:
    https://rcmes.jpl.nasa.gov/query-api/query.php?
'''
# Needed Python 2/3 urllib compatability
try:
    from urllib.parse import urlencode
    from urllib.request import urlopen
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen

import re
import json
import numpy as np
import numpy.ma as ma
from datetime import datetime
import calendar
from ocw.dataset import Dataset


URL = 'http://rcmes.jpl.nasa.gov/query-api/query.php?'


def get_parameters_metadata():
    '''Get the metadata of all parameter from RCMED.

    :returns: Dictionary of information for each parameter stored in one list
    :rtype: :class:`list` of :class:`dict`
    '''

    param_info_list = []
    url = URL + "&param_info=yes"
    string = urlopen(url)
    data_string = string.read().decode('utf-8')
    json_format_data = json.loads(data_string)
    fields_name = json_format_data['fields_name']
    data = json_format_data['data']
    for row in data:
        dic = {}
        for name in fields_name:
            dic[name] = row[fields_name.index(name)]
        param_info_list.append(dic)

    return param_info_list


def _make_mask_array(values, parameter_id, parameters_metadata):
    '''Created masked array to deal with missing values

    :param values: Numpy array of values which may contain missing values
    :type values: Numpy array
    :param parameter_id: Parameter's id
    :type parameter_id: Integer
    :param parameters_metadata: Metadata for all parameters
    :type parameters_metadata: List of dictionaries

    :returns: Masked array of values
    :rtype: Masked array
    '''

    for each in parameters_metadata:
        if str(each['parameter_id']) == str(parameter_id):
            missing_values = each['missingdataflag'].encode()
            break
    missing_values = float(missing_values)
    values = ma.masked_array(values, mask=(values == missing_values))

    return values


def _reshape_values(values, unique_values):
    '''Reshape values into 4D array.

    :param values: Raw values data
    :type values: numpy array
    :param unique_values: Tuple of unique latitudes, longitudes and times data.
    :type unique_values: Tuple

    :returns: Reshaped values data
    :rtype: Numpy array
    '''

    lats_len = len(unique_values[0])
    lons_len = len(unique_values[1])
    times_len = len(unique_values[2])

    values = values.reshape(times_len, lats_len, lons_len)

    return values


def _calculate_time(unique_times, time_step):
    '''Convert each time to the datetime object.

    :param unique_times: Unique time data
    :type unique_times: String
    :param time_step: Time step
    :type time_step: String

    :returns: Unique datetime objects of time data
    :rtype: Numpy array
    '''

    time_format = "%Y-%m-%d %H:%M:%S"
    unique_times = np.array(
        [datetime.strptime(time.decode('utf-8'), time_format)
                           for time in unique_times])
    # There is no need to sort time.
    # This function may required still in RCMES
    # unique_times.sort()
    # This function should be moved to the data_process.

    return unique_times


def _make_unique(lats, lons, times):
    '''Find the unique values of input data.

    :param lats: lats
    :type lats: Numpy array
    :param lons: lons
    :type lons: Numpy array
    :param times: times
    :type times: Numpy array

    :returns: Unique numpy arrays of latitudes, longitudes and times
    :rtype: Tuple
    '''

    unique_lats = np.unique(lats)
    unique_lons = np.unique(lons)
    unique_times = np.unique(times)

    return (unique_lats, unique_lons, unique_times)


def _get_data(url):
    '''Reterive data from database.

    :param url: url to query from database
    :type url: String

    :returns: Latitudes, longitudes, times and values data
    :rtype: (Numpy array, Numpy array, Numpy array, Numpy array)
    '''

    string = urlopen(url)
    data_string = string.read()
    index_of_data = re.search(b'data: \r\n', data_string)
    data = data_string[index_of_data.end():len(data_string)]
    data = data.split(b'\r\n')

    lats = []
    lons = []
    #levels = []
    values = []
    times = []

    # Because the last row is empty, "len(data)-1" is used.
    for i in range(len(data) - 1):
        row = data[i].split(b',')
        lats.append(np.float32(row[0]))
        lons.append(np.float32(row[1]))
        # Level is not currently supported in Dataset class.
        # levels.append(np.float32(row[2]))
        times.append(row[3])
        values.append(np.float32(row[4]))

    lats = np.array(lats)
    lons = np.array(lons)
    times = np.array(times)
    values = np.array(values)

    return lats, lons, times, values


def _beginning_of_date(time, time_step):
    '''Calculate the beginning of given time, based on time step.

    :param time: Given time
    :type time: Datetime
    :param time_step: Time step (monthly or daily)
    :type time_step: String

    :returns: Beginning of given time
    :rtype: Datetime
    '''

    if time_step.lower() == 'monthly':
        if time.day != 1:
            time = datetime(time.year, time.month, 1)
    elif time_step.lower() == 'daily':
        if time.hour != 0 or time.minute != 0 or time.second != 0:
            time = datetime(time.year, time.month, time.day, 00, 00, 00)

    return time


def _end_of_date(time, time_step):
    '''Calculate the end of given time, based on time step.

    :param time: Given time
    :type time: Datetime
    :param time_step: Time step (monthly or daily)
    :type time_step: String

    :returns: End of given time
    :rtype: Datetime
    '''

    last_day_of_month = calendar.monthrange(time.year, time.month)[1]
    if time_step.lower() == 'monthly':
        time = datetime(time.year, time.month, last_day_of_month)
    elif time_step.lower() == 'daily':
        time = datetime(time.year, time.month, time.day, 23, 59, 59)

    return time


def _generate_query_url(dataset_id, parameter_id, min_lat, max_lat, min_lon, max_lon, start_time, end_time, time_step):
    '''Generate the url to query from database

    :param dataset_id: Dataset id.
    :type dataset_id: Integer
    :param parameter_id: Parameter id
    :type parameter_id: Integer
    :param min_lat: Minimum latitude
    :type min_lat: Float
    :param max_lat: Maximum latitude
    :type max_lat: Float
    :param min_lon: Minimum longitude
    :type min_lon: Float
    :param max_lon: Maximum longitude
    :type max_lon: Float
    :param start_time: Start time
    :type start_time: Datetime
    :param end_time: End time
    :type end_time: Datetime
    :param time_step: Time step
    :type time_step: String

    :returns: url to query from database
    :rtype: String
    '''

    start_time = _beginning_of_date(start_time, time_step)
    end_time = _end_of_date(end_time, time_step)
    start_time = start_time.strftime("%Y%m%dT%H%MZ")
    end_time = end_time.strftime("%Y%m%dT%H%MZ")

    query = [('datasetId', dataset_id), ('parameterId', parameter_id), ('latMin', min_lat), ('latMax', max_lat),
             ('lonMin', min_lon), ('lonMax', max_lon), ('timeStart', start_time), ('timeEnd', end_time)]

    query_url = urlencode(query)
    url_request = URL + query_url

    return url_request


def _get_parameter_info(parameters_metadata, parameter_id):
    '''General information for given parameter id.

    :param parameters_metadata: Metadata for all parameters
    :type parameters_metadata: List of dictionaries
    :param parameter_id: Parameter id
    :type parameter_id: Integer

    :returns: Database name, time step, realm, instrument, start_date, end_date and unit for given parameter
    :rtype: (string, string, string, string, string, string, string)
    '''

    for dic in parameters_metadata:
        if int(dic['parameter_id']) == parameter_id:
            database = dic['database']
            time_step = dic['timestep']
            realm = dic['realm']
            instrument = dic['instrument']
            start_date = dic['start_date']
            end_date = dic['end_date']
            unit = dic['units']

    return (database, time_step, realm, instrument, start_date, end_date, unit)


def parameter_dataset(dataset_id, parameter_id, min_lat, max_lat, min_lon, max_lon, start_time, end_time, name=''):
    '''Get data from one database(parameter).

    :param dataset_id: Dataset id.
    :type dataset_id: :class:`int`

    :param parameter_id: Parameter id
    :type parameter_id: :class:`int`

    :param min_lat: Minimum latitude
    :type min_lat: :class:`float`

    :param max_lat: Maximum latitude
    :type max_lat: :class:`float`

    :param min_lon: Minimum longitude
    :type min_lon: :class:`float`

    :param max_lon: Maximum longitude
    :type max_lon: :class:`float`

    :param start_time: Start time
    :type start_time: :class:`datetime.datetime`

    :param end_time: End time
    :type end_time: :class:`datetime.datetime`

    :param name: (Optional) A name for the loaded dataset.
    :type name: :mod:`string`

    :returns: An OCW Dataset object contained the requested data from RCMED.
    :rtype: :class:`dataset.Dataset`
    '''

    parameters_metadata = get_parameters_metadata()
    parameter_name, time_step, _, _, _, _, parameter_units = _get_parameter_info(
        parameters_metadata, parameter_id)

    lats, lons, times, values = \
        _coalesce_data(dataset_id, parameter_id, min_lat, max_lat, min_lon, max_lon,
                       start_time, end_time, time_step)

    unique_lats_lons_times = _make_unique(lats, lons, times)
    unique_times = _calculate_time(unique_lats_lons_times[2], time_step)
    values = _reshape_values(values, unique_lats_lons_times)
    values = _make_mask_array(values, parameter_id, parameters_metadata)

    origin = {
        'source': 'rcmed',
        'dataset_id': dataset_id,
        'parameter_id': parameter_id
    }

    return Dataset(unique_lats_lons_times[0],
                   unique_lats_lons_times[1],
                   unique_times,
                   values,
                   variable=parameter_name,
                   units=parameter_units,
                   name=name,
                   origin=origin)


def _coalesce_data(dataset_id, parameter_id, min_lat, max_lat, min_lon, max_lon,
                       start_time, end_time, time_step):

    """
    Refer to this JIRA:  https://issues.apache.org/jira/browse/CLIMATE-744

    Sometimes RCMED does not seem to return the entire data set when the requested
    range of data and / or number of data points are very large.  This method breaks
    the single large query into several smaller queries and then appends the results.

    :param dataset_id:  The RCMED dataset ID.
    :param parameter_id:  The parameter ID within the RCMED dataset.
    :param min_lat: The minimum lat of the dataset boundary.
    :param max_lat: The maximum lat of the dataset boundary.
    :param min_lon: The minimum lon of the dataset boundary.
    :param max_lon: The maximum lon of the dataset boundary.
    :param start_time: The start datetime of the dataset boundary.
    :param end_time: The end datetime of the dataset boundary.
    :param time_step: The timestep to use when segmenting the datetime boundary.
    :return:  lats, lons, times, and values for the requested dataset / parameter from RCMED.
    """

    lats = None
    lons = None
    times = None
    values = None

    # This is a magic number which strikes a balance between making an excessive number of
    # calls to RCMED (e.g. 1) and RCMED not sending back the full data set.
    step = 4

    current_start = start_time
    current_end = min(end_time, datetime(current_start.year + step, 12, 31))

    while True:

        url = _generate_query_url(dataset_id, parameter_id, min_lat,
                                  max_lat, min_lon, max_lon, current_start, current_end, time_step)

        tmp_lats, tmp_lons, tmp_times, tmp_values = _get_data(url)

        if lats is None:
            lats = tmp_lats
        else:
            lats = np.append(lats, tmp_lats)

        if lons is None:
            lons = tmp_lons
        else:
            lons = np.append(lons, tmp_lons)

        if times is None:
            times = tmp_times
        else:
            times = np.append(times, tmp_times)

        if values is None:
            values = tmp_values
        else:
            values = np.append(values, tmp_values)

        if current_end == end_time:
            break

        current_start = datetime(current_end.year + 1, 1, 1)
        current_end = min(end_time, datetime(current_start.year + step, 12, 31))


    return lats, lons, times, values
