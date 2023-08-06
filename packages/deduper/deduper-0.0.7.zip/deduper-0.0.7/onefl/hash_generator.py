"""
Goal: Store functions used for converting PHI data into hashed strings

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""

import os
import sys
import pandas as pd
import multiprocessing as mp
import traceback
from dateutil import parser as dp
from onefl.rules import AVAILABLE_RULES_MAP as rulz
from onefl import utils
from onefl.exc import ConfigErr
from onefl.normalized_patient import NormalizedPatient  # noqa

pd.set_option('display.width', 1500)

COL_PATID = 'patid'
COL_FIRST = 'first'
COL_LAST = 'last'
COL_DOB = 'dob'
COL_RACE = 'race'
COL_SEX = 'sex'
REQUIRED_COLS = [COL_PATID, COL_FIRST, COL_LAST, COL_DOB, COL_RACE, COL_SEX]

VALID_RACE_VALS = ['',
                   '01', '02', '03', '04', '05', '06', '07',
                   '1', '2', '3', '4', '5', '6', '7',
                   'NI', 'UN', 'OT']
VALID_SEX_VALS = ['', 'A', 'F', 'M', 'NI', 'UN', 'OT']

# How many processes to use?
NUM_CPUS = max(1, mp.cpu_count() - 2)


class HashGenerator():
    log = None

    @classmethod
    def configure_logger(cls, logger):
        cls.log = logger

    @staticmethod
    def format_race(val):
        # prevent "Excel errors"
        if str(val) in ['1', '2', '3', '4', '5', '6', '7']:
            return '{:0>2}'.format(val)
        return val

    @staticmethod
    def format_date(val):
        """ Convenience method to try multiple date formats """
        if not val:
            return None
        try:
            parsed_date = dp.parse(val)
        except Exception as exc:
            print("Unable to parse the date: {}".format(val))
            raise exc

        return parsed_date.strftime('%Y-%m-%d')

    @staticmethod
    def _process_row_series(row, rule, pattern, required_attr, config):
        """
        Compute the sha256 string for one rule.

        .. seealso::
            :`_process_frame`

        :param config: dictionary with run-time parameters
        :rtype: string
        :return sha_string:
        """
        COLUMN_MAP = config['COLUMN_MAP']

        patient = NormalizedPatient(
            patid=row[COLUMN_MAP[COL_PATID]],
            pat_first_name=row[COLUMN_MAP[COL_FIRST]],
            pat_last_name=row[COLUMN_MAP[COL_LAST]],
            pat_birth_date=HashGenerator.format_date(
                row[COLUMN_MAP[COL_DOB]]),
            pat_sex=row[COLUMN_MAP[COL_SEX]],
            pat_race=HashGenerator.format_race(
                row[COLUMN_MAP[COL_RACE]])
        )

        if not patient.has_all_data(required_attr):
            # print("Skip hashing patient [{}] due to missing data for rule [{}]".format(patient.patid, rule))  # noqa
            return ''

        raw = pattern.format(patient) + config['SALT']
        sha_string = utils.apply_sha256(raw)
        # print("For patient [{}] (rule {}): {}, hash_string= {}".format(patient.patid, rule, raw, sha_string))  # noqa

        return sha_string

    @staticmethod
    def _process_frame(df_source, config):
        """
        Create a result frame

        .. seealso::
            :`_process_row_series`
            :`generate`

        Reminder:
            - apply() works on a row / column basis of a DataFrame
            - applymap() works element-wise on a DataFrame
            - map() works element-wise on a Series

        """
        df = pd.DataFrame()

        # keep the patid from the source
        df['PATID'] = df_source['patid']

        for i, rule in enumerate(rulz):
            rule_data = rulz.get(rule)
            pattern = rule_data['pattern']
            required_attr = rule_data['required_attr']

            df[rule] = df_source.apply(
                lambda x: HashGenerator._process_row_series(
                    x, rule, pattern,
                    required_attr,
                    config), axis=1)
        # print("Processed frame: \n{}".format(df))
        return df

    @classmethod
    def _validate_config(cls, config):
        """
        Helper method for preventing config errors
        """
        COLUMN_MAP = config.get('COLUMN_MAP', None)

        if COLUMN_MAP is None:
            raise ConfigErr("Please verify that the config specifies the `COLUMN_MAP` parameter!")  # noqa

        # Verify that every required column is mapped
        CONFIGURED_COLS = list(COLUMN_MAP.keys())
        diff = list(set(REQUIRED_COLS).difference(CONFIGURED_COLS))
        cls.log.info('REQUIRED_COLS: {}'.format(REQUIRED_COLS))
        cls.log.info('CONFIGURED_COLS: {}'.format(CONFIGURED_COLS))

        if len(diff) > 0:
            raise ConfigErr('Please verify that the config specifies every column in the `COLUMN_MAP` parameter! Missing: {}'.format(diff))  # noqa

        enabled_rules = config.get('ENABLED_RULES', None)

        if not enabled_rules:
            raise ConfigErr('Please verify that the config specifies the `ENABLED_RULES` parameter!')  # noqa

        for rule_code in enabled_rules:
            if rule_code not in rulz:
                raise ConfigErr('Invalid rule: [{}]! Available codes are: {}'
                                .format(rule_code, rulz.keys()))

    @classmethod
    def generate(cls, config, inputdir, outputdir, ask=True):
        """
        Read the "phi.csv" file and generate "phi_hashes.csv"
        containing two (or more) sha256 strings for each line
        in the input file.

        This method is invoked from

        .. seealso::

            run_hasher.py

        :param inputdir: directory name for the source file
        :param outputdir: directory name for generated file

        :rtype: DataFrame
        :return the frame with hashes of the PHI data

        Columns:
            - patid
            - sha_rule_1 (first_last_dob_race)
            - sha_rule_2 (first_last_dob_sex)

        """
        cls._validate_config(config)

        EXPECTED_COLS = list(config['COLUMN_MAP'].values())
        ENABLED_RULES = config.get('ENABLED_RULES')

        in_file = os.path.join(inputdir, config['IN_FILE'])
        cls.log.info("Using [{}] as source file".format(in_file))
        cls.log.info("Using [{}] as record separator"
                     .format(config['IN_DELIMITER']))
        cls.log.info("Using [{}] as salt".format(config['SALT']))
        cls.log.info("Expecting input file to contain columns: {}"
                     .format(EXPECTED_COLS))

        if ask:
            confirmed = utils.ask_yes_no(
                "Continue hash procedure to create files in the [{}] folder?"
                .format(outputdir))
            if not confirmed:
                sys.exit("If you say so...")

        reader = None

        try:
            reader = pd.read_csv(in_file,
                                 sep=config['IN_DELIMITER'],
                                 dtype=object,
                                 skipinitialspace=True,
                                 skip_blank_lines=True,
                                 usecols=EXPECTED_COLS,
                                 chunksize=config['LINES_PER_CHUNK'],
                                 iterator=True)
            cls.log.info("Reading data from file: {} ({})"
                         .format(in_file, utils.get_file_size(in_file)))

        except ValueError as exc:
            cls.log.info("Please check if the actual column names in [{}] "
                         .format(in_file) +
                         "match the configured column names: {}."
                         .format(sorted(EXPECTED_COLS)))
            cls.log.error("Error: {}".format(exc))

        frames = []
        pool = mp.Pool(processes=NUM_CPUS)
        jobs = []

        for index, df_source in enumerate(reader):
            cls.log.info("Processing {} lines of frame {}"
                         .format(config['LINES_PER_CHUNK'], index))
            df_source.fillna('', inplace=True)

            # validate the values constrained to set
            invalid_race = df_source.loc[~df_source[COL_RACE].isin(VALID_RACE_VALS)]  # noqa
            invalid_sex = df_source.loc[~df_source[COL_SEX].isin(VALID_SEX_VALS)]  # noqa

            if len(invalid_race) > 0:
                cls.log.info("Please check race: \n{}".format(invalid_race))
                raise Exception("The input file contains invalid value for `race` column. Please review the specs.")  # noqa
            if len(invalid_sex) > 0:
                cls.log.warning("Please check sex: \n{}".format(invalid_sex))
                raise Exception("The input file contains invalid value for `sex` column. Please review the specs.")  # noqa

            job = utils.apply_async(pool,
                                    HashGenerator._process_frame,
                                    (df_source, config))
            jobs.append(job)

        job_count = len(jobs)
        cls.log.info("Total multiproc jobs: {}".format(job_count))

        # collect the results
        for index, job in enumerate(jobs):
            try:
                frames.append(job.get())
                if index % 10 == 0:
                    cls.log.info("Got results for frame {} (out of {})"
                                 .format(index, job_count))
            except Exception as exc:
                cls.log.error("Job [{}] error: {}".format(index, exc))
                cls.log.error(traceback.format_exc())

        pool.close()
        pool.join()
        cls.log.info("Got all {} frames. Concatenating...".format(job_count))
        df = pd.concat(frames, ignore_index=True)

        # Concatenation can re-order columns so we need to enforce the order
        out_columns = ['PATID']
        out_columns.extend(ENABLED_RULES)

        out_file = os.path.join(outputdir, config['OUT_FILE'])
        utils.frame_to_file(df[out_columns], out_file,
                            delimiter=config['OUT_DELIMITER'])

        cls.log.info("Wrote output file: {} ({} data rows, {})"
                     .format(out_file,
                             len(df),
                             utils.get_file_size(out_file)))

        # count how many patients did not get a hash generated
        # query_no_hashes = df.query('m == "" & n == ""')
        query_no_hashes = ' & '.join(['{} == ""'.format(rule)
                                      for rule in ENABLED_RULES])
        df_no_hashes = df.query(query_no_hashes)
        cls.log.info("The result file contains [{}] patients without hashes."
                     .format(len(df_no_hashes)))
        if len(df_no_hashes) > 0:
            cls.log.info(df_no_hashes.head())
        return True
