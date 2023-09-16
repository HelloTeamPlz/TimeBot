import os
from nextcord.utils import format_dt
import dateutil.parser as dparser
from datetime import datetime, timedelta, timezone
import easyocr
import re
from nextcord.utils import format_dt

class StructureBot:
    
    def __init__() -> None:
        pass
    
    def get_channel_id(channel_name):
        """
        gets the channel id from env file
        """
        channel_id = os.environ.get(f"{channel_name}")
        return int(channel_id)
    
    def to_unix_time(date_time):
        unix_time = int(datetime.timestamp(date_time))
        return unix_time

    def new_Site(time):
        """
        convert input to datetime object, add 35 minutes to the time, return the new time in 24-hour format 
        """
        time = datetime.strptime(time, '%H:%M')
        new_time = time + timedelta(minutes=35)
        return new_time.strftime('%H:%M')

    def timer(time):
        """
        given a string that looks like text, text and time stamp split on the "," parse the list to find the timestamp convert the timestamp into short and relitive date format
        for discod and return a tuple with all the desired values
        take curr unix time - future unix time + 900 (15 minm)
        """
        sysName = time.split(",")
        structure_timer = dparser.parse(time, fuzzy=True)
        short_date_time = format_dt(structure_timer, "f")
        relative_date = format_dt(structure_timer, "R")
        unix_structure_timer = StructureBot.to_unix_time(structure_timer)
        current_unix_time = StructureBot.to_unix_time(datetime.now(timezone.utc))
        seconds_till_timer = unix_structure_timer - current_unix_time + 900
        return (sysName[0], structure_timer,seconds_till_timer)

    
    def date_from_list(ocr_results):
        for i in ocr_results:
            result_ints = re.sub(r'[^0-9. ]', '', i)
        if len(result_ints) >= 10:
            result_ints = re.sub(r'[^0-9. ]', '', i)
            parts = result_ints.split('.')
            result_ints = '.'.join(parts[:-1])
            input_string = result_ints.strip()
            datetime_format = '%Y.%m.%d %H.%M'

            parsed_datetime =  datetime.strptime(input_string, datetime_format)
            return parsed_datetime

    def read_img(image_path):
        reader = easyocr.Reader(['en'], gpu = False)
        preprocessed_image = image_path
        results = reader.readtext(preprocessed_image, detail=0)
        return results
    
    def ocr_timer(timer):
        unix_structure_timer = StructureBot.to_unix_time(timer)
        current_unix_time = StructureBot.to_unix_time(datetime.now(timezone.utc))
        seconds_till_timer = unix_structure_timer - current_unix_time + 900
        return seconds_till_timer