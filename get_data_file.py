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


def get_xbrl(company):
    # gets data files from a given Company instance and returns the parse xbrl
    results = company.get_data_files_from_10K("XML", isxml=True)
    xbrl = XBRL(results[0])

    xbrl_files = [XBRLElement(file).to_dict() for file in xbrl.relevant_children_parsed]

    segment_xbrl = filter_segment_data(xbrl_files)
    for elem in segment_xbrl:
        elem['company'] = company.name
        elem['cik'] = company.cik

    return segment_xbrl


def filter_segment_data(xbrl_files):
    # filter for correct tag
    segment_xbrl = [elem for elem in xbrl_files if
                    elem.get('name') == 'Revenue From Contract With Customer Excluding Assessed Tax']

    # filter for more info than just the year: "FD2017Q4YTD" gets dropped
    segment_xbrl = [elem for elem in segment_xbrl if len(elem.get('context_ref')) > 11]

    # filter for context that contains "Segment" or "ProductOrService"
    segment_xbrl = [elem for elem in segment_xbrl if
                    elem.get('context_ref').find('Segment') != -1 or
                    elem.get('context_ref').find('ProductOrService') != -1]

    return segment_xbrl


def xbrl_to_df(xbrl_list):
    df = pd.DataFrame(xbrl_list)
    df = df.drop(columns='name')
    df = df.rename(columns={'unit_ref': 'unit'})
    df['context'] = None
    df['prefix'] = None
    df['year'] = None
    df['quarters'] = None

    for index, row in df.iterrows():
        split_context = row['context_ref'].split('_')

        row['context'] = ' '.join(split_context[1:])

        # parse the dates
        row['prefix'] = split_context[0][0:2]
        row['year'] = split_context[0][2:6]
        row['quarters'] = split_context[0][6:]

    df = df.drop(columns='context_ref')

    return df


def main():
    # establish a list of companies to extract data from
    company_list = [('AMAZON COM INC', '0001018724'), ('Apple Inc.', '0000320193')]

    # iterate through the companies, calling the get_xbrl function on each
    xbrl_files = [get_xbrl(Company(pair[0], pair[1])) for pair in company_list]

    # fill pandas with the segment data
    segment_df = xbrl_to_df(xbrl_files[0])
    print(segment_df.describe())
    print(segment_df.head())


if __name__ == '__main__':
    main()
