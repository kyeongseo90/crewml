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
import traceback
from simul.pairing import flclean as fl
from config import config
from simul.pairing import flcat
from simul.pairing import dutygen as dg
from simul.pairing import pairinggen as pg
from simul.pairing import costcal as cc
import common as st
from data import feature as fet


def main():
    '''
    Main function to execute crewml simul functions

    Returns
    -------
    None.

    '''
    try:
        logger = logging.getLogger(__name__)

        logger.info("Starting main")

        ch = config.ConfigHolder(st.RESOURCE_DIR+"pairing_config.ini")

        # Create FlightCleaner object, load the flights, use the timezone
        # to convert the local departure and arrival time to
        # UTC time
        timezone_file = ch.getValue("timezone_file")
        clean_output = ch.getValue("clean_output_file")
        dutygen_files = ch.getValue("dutygen_files").split(",")
        raw_input_file = ch.getValue("raw_input_file")

        elements = ch.getValue("flight_features")
        elements = elements.split(",")

        feature = fet.Feature(file_name=raw_input_file)

        logger.info("Creating FlightCleaner object")
        fc = fl.FlightCleaner(timezone_file_name=timezone_file,
                              feature=feature,
                              output_file_name=clean_output
                              )

        logger.info("Starting FlightCleaner process to clean the flight data")
        fc.process()
        logger.info("Finished FlightCleaner process to clean the flight data")

        dl_fa_bases = ch.getValue("dl_fa_bases")
        dl_fa_non_bases = ch.getValue("dl_fa_non_bases")
        classify_output_files = ch.getValue("cat_output_files").split(",")
        logger.info("Creating FlightCategorizer object")
        fc = flcat.FlightCategorizer(
            dl_fa_bases, dl_fa_non_bases, clean_output, classify_output_files)
        logger.info(
            "Starting FlightCategorizer process to classify the flights")
        fc.process()
        logger.info(
            "Finished FlightCategorizer process to classify the flights")

        logger.info("Creating DutyGenerator object")
        d = dg.DutyGenerator(dutygen_files)
        logger.info("Starting DutyGenerator process to create Duties")
        d.process()
        logger.info("Finished DutyGenerator process to create Duties")

        pairing_gen_output_file = ch.getValue("pairing_gen_output_file")
        pairing_gen_missing_files = ch.getValue(
            "pairing_gen_missing_files").split(",")
        logger.info("Creating PairingGenerator object")
        pgen = pg.PairingGenerator(
            dutygen_files[2],
            pairing_gen_missing_files,
            pairing_gen_output_file)
        logger.info("Starting PairingGenerator process to create Pairings")
        pgen.process()
        logger.info("Finished PairingGenerator process to create Pairings")

        cost_cal_input_file = ch.getValue("cost_cal_input_file")
        cost_cal_output_file = ch.getValue("cost_cal_output_file")
        logger.info("Creating CostCalculator object")
        costcal = cc.CostCalculator(
            cost_cal_input_file, cost_cal_output_file, dl_fa_bases)
        logger.info(
            "Starting CostCalculator process to create cost for each fligh \
            in the Pairings")
        costcal.process()
        logger.info(
            "Finished CostCalculator process to create cost for \
                each fligh in the Pairings")

        logger.info("Finished main")
    except Exception as e:
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    import logging.config
    logging.config.fileConfig(st.RESOURCE_DIR+'logging.ini',
                              disable_existing_loggers=False)

    main()
