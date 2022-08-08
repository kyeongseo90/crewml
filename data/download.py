'''
__author__=Mani Malarvannan

MIT License

Copyright (c) 2020 crewml

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from pathlib import Path
import zipfile
import hashlib
import boto3
import os
import logging

from exception import CrewmlDataError
from common import ROOT_DIR
from common import RESOURCE_DIR
from config import config
from exception import CrewmlValueError

    def download(self):
        '''
        Downloads the data and performs the sha256_hash on the file,
        compares it with the already calculated sha256_hash
        from the config file. If the value doesn't match
        raises CrewmlDataError

        Raises
        ------
        CrewmlDataError
            If the file already exist and overwrite=False.
            If the downloaded signature doesn't match with the already
            calculated signature

        Returns
        -------
        None.

        '''
        self.logger = logging.getLogger(__name__)
        if name != "flight" and name != "pairing":
            raise CrewmlValueError("Valid values are flight or pairing")
        self.name = name
        self.overwrite = overwrite
        self.config = config.ConfigHolder(RESOURCE_DIR+"pairing_config.ini")

        if year is not None:
            self.year = year
        else:
            self.year = self.config.getValue("flight_year")
        if month is not None:
            self.month = month
        else:
            self.month = self.config.getValue("flight_month")
            
        self.zip_file_name = str(self.year)+"_"+str(self.month)+".zip"
        self.csv_file_name = str(self.year)+"_"+str(self.month)+".csv"
        
        self.download_dir = ROOT_DIR+"/crewml/data/files/raw_file/"
        
        zip_file = Path(self.download_dir+self.zip_file_name)
        csv_file = Path(self.download_dir+self.csv_file_name)
        

        if zip_file.is_file() and self.overwrite is False:
            raise CrewmlDataError(
                str(zip_file)+" already exist. \
                    Either delete it or set overwrite=True")
        elif zip_file.is_file() and self.overwrite is True:
            os.remove(zip_file)
            os.remove(csv_file)
        
        aws_region=self.config.getValue("aws_region")
        os.rename("./"+self.zip_file_name,
                  self.download_dir+self.zip_file_name)

        with zipfile.ZipFile(self.download_dir+self.zip_file_name, 'r') \
                as zip_ref:
            zip_ref.extractall(self.download_dir)

        sha256_hash = hashlib.sha256()
        f = open(self.download_dir+self.csv_file_name, 'r')
        data = f.read()
        sha256_hash.update(data.encode("utf-8"))

        download_file_sig = sha256_hash.hexdigest()
        real_sig = self.config.getValue(self.csv_file_name)

        self.logger.info("download_file_sig=", download_file_sig)
        self.logger.info("real_sig=", real_sig)

        if download_file_sig != real_sig:
            raise CrewmlDataError(
                "Downloaded file might be corrupted, delete the \
                    file and download it again")


# test
d.download()
