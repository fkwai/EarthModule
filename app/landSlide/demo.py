import json
import pandas as pd

file='/mnt/sdb/landSlideDB/conf8/Landsat7-kernal9-day200/site0000'

with open(file) as json_file:
    data = json.load(json_file)
df = pd.DataFrame(data)