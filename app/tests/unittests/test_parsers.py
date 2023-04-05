import pytest

from app.parsers import parse_fastq_name, parse_miseq_run_name


def test_parse_fastq_name():
    fastq_name_example = '1111-11_S11_L001_R1_001.fastq.gz'
    parse_fastq_name(fastq_name_example)


def test_parse_fastq_wdh_name():
    fastq_wdh_name_example = '2160-22-wdh_S10_L001_R2_001.fastq.gz'
    parse_fastq_name(fastq_wdh_name_example)


def test_parse_miseq_run_name():
    miseq_name_example = '220101_M01011_0111_000000000-A11A1'
    parse_miseq_run_name(miseq_name_example)

