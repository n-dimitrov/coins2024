import os
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError

flags = {
    "Andorra": ":flag-ad:",
    "Austria": ":flag-at:",
    "Belgium": ":flag-be:",
    "Croatia": ":flag-hr:",
    "Cyprus": ":flag-cy:",
    "Estonia": ":flag-ee:",
    "Euro area countries": "Euro area countries",
    "Finland": ":flag-fi:",
    "France": ":flag-fr:",
    "Germany": ":flag-de:",
    "Greece": ":flag-gr:",
    "Ireland": ":flag-ie:",
    "Italy": ":flag-it:",
    "Latvia": ":flag-lv:",
    "Lithuania": ":flag-lt:",
    "Luxembourg": ":flag-lu:",
    "Malta": ":flag-mt:",
    "Monaco": ":flag-mc:",
    "Netherlands": ":flag-nl:",
    "Portugal": ":flag-pt:",
    "San Marino": ":flag-sm:",
    "Slovakia": ":flag-sk:",
    "Slovenia": ":flag-si:",
    "Spain": ":flag-es:",
    "Vatican City": ":flag-va:"
}

series_names = {
    "AND-01": "Andorra 1",
    "AUT-01": "Austria 1",
    "BEL-01": "Belgium 1",
    "BEL-02": "Belgium 2",
    "BEL-03": "Belgium 3",
    "CYP-01": "Cyprus 1",
    "DEU-01": "Germany 1",
    "ESP-01": "Spain 1",
    "ESP-02": "Spain 2",
    "ESP-03": "Spain 3",
    "EST-01": "Estonia 1",
    "FIN-01": "Finland 1",
    "FIN-02": "Finland 2",
    "FRA-01": "France 1",
    "FRA-02": "France 2",
    "GRC-01": "Greece 1",
    "HRV-01": "Croatia 1",
    "IRL-01": "Ireland 1",
    "ITA-01": "Italy 1",
    "LTU-01": "Lithuania 1",
    "LUX-01": "Luxembourg 1",
    "LVA-01": "Latvia 1",
    "MCO-01": "Monaco 1",
    "MCO-02": "Monaco 2",
    "MLT-01": "Malta 1",
    "NLD-01": "Netherlands 1",
    "NLD-02": "Netherlands 2",
    "PRT-01": "Portugal 1",
    "SMR-01": "San Marino 1",
    "SMR-02": "San Marino 2",
    "SVK-01": "Slovakia 1",
    "SVN-01": "Slovenia 1",
    "VAT-01": "Vatican City 1",
    "VAT-02": "Vatican City 2",
    "VAT-03": "Vatican City 3",
    "VAT-04": "Vatican City 4",
    "VAT-05": "Vatican City 5",
    "CC-2004": "CC 2004",
    "CC-2005": "CC 2005",
    "CC-2006": "CC 2006",
    "CC-2007": "CC 2007",
    "CC-2007-TOR": "CC 2007 TOR",
    "CC-2008": "CC 2008",
    "CC-2009": "CC 2009",
    "CC-2009-EMU": "CC 2009 EMU",
    "CC-2010": "CC 2010",
    "CC-2011": "CC 2011",
    "CC-2012": "CC 2012",
    "CC-2012-TYE": "CC 2012 TYE",
    "CC-2013": "CC 2013",
    "CC-2014": "CC 2014",
    "CC-2015": "CC 2015",
    "CC-2015-EUF": "CC 2015 EUF",
    "CC-2016": "CC 2016",
    "CC-2017": "CC 2017",
    "CC-2018": "CC 2018",
    "CC-2019": "CC 2019",
    "CC-2020": "CC 2020",
    "CC-2021": "CC 2021",
    "CC-2022": "CC 2022",
    "CC-2022-ERA": "CC 2022 ERA",
    "CC-2023": "CC 2023"
}

series_names_info = {
    "AND-01": "Andorra 1",
    "AUT-01": "Austria 1",
    "BEL-01": "Belgium 1",
    "BEL-02": "Belgium 2",
    "BEL-03": "Belgium 3",
    "CYP-01": "Cyprus 1",
    "DEU-01": "Germany 1",
    "ESP-01": "Spain 1",
    "ESP-02": "Spain 2",
    "ESP-03": "Spain 3",
    "EST-01": "Estonia 1",
    "FIN-01": "Finland 1",
    "FIN-02": "Finland 2",
    "FRA-01": "France 1",
    "FRA-02": "France 2",
    "GRC-01": "Greece 1",
    "HRV-01": "Croatia 1",
    "IRL-01": "Ireland 1",
    "ITA-01": "Italy 1",
    "LTU-01": "Lithuania 1",
    "LUX-01": "Luxembourg 1",
    "LVA-01": "Latvia 1",
    "MCO-01": "Monaco 1",
    "MCO-02": "Monaco 2",
    "MLT-01": "Malta 1",
    "NLD-01": "Netherlands 1",
    "NLD-02": "Netherlands 2",
    "PRT-01": "Portugal 1",
    "SMR-01": "San Marino 1",
    "SMR-02": "San Marino 2",
    "SVK-01": "Slovakia 1",
    "SVN-01": "Slovenia 1",
    "VAT-01": "Vatican City 1",
    "VAT-02": "Vatican City 2",
    "VAT-03": "Vatican City 3",
    "VAT-04": "Vatican City 4",
    "VAT-05": "Vatican City 5",
    "CC-2004": "Commemorative 2004",
    "CC-2005": "Commemorative 2005",
    "CC-2006": "Commemorative 2006",
    "CC-2007": "Commemorative 2007",
    "CC-2007-TOR": "Commemorative 2007 / 50th anniversary of the Treaty of Rome",
    "CC-2008": "Commemorative 2008",
    "CC-2009": "Commemorative 2009",
    "CC-2009-EMU": "Commemorative 2009 / 10th anniversary of Economic and Monetary Union",
    "CC-2010": "Commemorative 2010",
    "CC-2011": "Commemorative 2011",
    "CC-2012": "Commemorative 2012",
    "CC-2012-TYE": "Commemorative 2012 / Ten years of the euro",
    "CC-2013": "Commemorative 2013",
    "CC-2014": "Commemorative 2014",
    "CC-2015": "Commemorative 2015",
    "CC-2015-EUF": "Commemorative 2015 EUF / The 30th anniversary of the EU flag",
    "CC-2016": "Commemorative 2016",
    "CC-2017": "Commemorative 2017",
    "CC-2018": "Commemorative 2018",
    "CC-2019": "Commemorative 2019",
    "CC-2020": "Commemorative 2020",
    "CC-2021": "Commemorative 2021",
    "CC-2022": "Commemorative 2022",
    "CC-2022-ERA": "Commemorative 2022 / 35 years of the Erasmus programme",
    "CC-2023": "Commemorative 2023"
}

s3 = boto3.client('s3')
bucket_name = "coins2024"

def upload_file_to_s3(file_name, object_name=None):
    if object_name is None:
        object_name = file_name

    try:
        s3.upload_file(file_name, bucket_name, object_name)
        print(f"File {file_name} uploaded to {bucket_name}/{object_name}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")

def get_file_from_s3(s3_key, local_cache_dir='.cache'):
    os.makedirs(local_cache_dir, exist_ok=True)
    local_file_path = os.path.join(local_cache_dir, s3_key)
    if os.path.exists(local_file_path):
        # print(f"File is already cached: {local_file_path}")
        return local_file_path
    
    print(f"Downloading {s3_key} from bucket {bucket_name}")
    s3.download_file(bucket_name, s3_key, local_file_path)
    return local_file_path

def download_file_from_s3(object_name, file_name=None, local_cache_dir='.cache'):
    if file_name is None:
        file_name = object_name

    os.makedirs(local_cache_dir, exist_ok=True)
    local_file_path = os.path.join(local_cache_dir, file_name)

    try:
        s3.download_file(bucket_name, object_name, local_file_path)
        print(f"File {object_name} downloaded from {bucket_name} to {local_file_path}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
    return local_file_path

def load_catalog():
    # print("Loading catalog")
    file = get_file_from_s3('catalog.csv')
    catalog_df = pd.read_csv(file)
    return catalog_df

def load_history():
    # print("Loading history")
    file = get_file_from_s3('history.csv')
    history_df = pd.read_csv(file)
    return history_df