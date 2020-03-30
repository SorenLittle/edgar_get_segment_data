import pandas as pd

from edgar import (
    Company,
    # XBRL,
    # XBRLElement,
)

from xbrl import (
    XBRL,
    XBRLElement
)

from pprint import pprint


def get_xbrl(company):
    # gets data files from a given Company instance and returns the parse xbrl
    results = company.get_data_files_from_10K("XML", isxml=True)
    xbrl = XBRL(results[0])

    xbrl_files = [XBRLElement(file).to_dict() for file in xbrl.relevant_children_parsed]

    segment_xbrl = filer_segment_data(xbrl_files)
    for elem in segment_xbrl:
        elem['company'] = company.name
        elem['cik'] = company.cik

    return segment_xbrl


def filer_segment_data(xbrl_files):
    segment_xbrl = [elem for elem in xbrl_files if
                    elem.get('name') == 'Revenue From Contract With Customer Excluding Assessed Tax']

    return segment_xbrl


def xbrl_to_db(xbrl_list):
    df = pd.DataFrame(xbrl_list)
    df = df.drop(columns='name')

    return df


def main():
    # establish a list of companies to extract data from
    company_list = [('AMAZON COM INC', '0001018724'), ('Apple Inc.', '0000320193')]

    # iterate through the companies, calling the get_xbrl function on each
    xbrl_files = [get_xbrl(Company(pair[0], pair[1])) for pair in company_list]
    pprint(xbrl_files)

    # fill pandas with the segment data
    segment_df = xbrl_to_db(xbrl_files[0])
    print(segment_df)


if __name__ == '__main__':
    main()
