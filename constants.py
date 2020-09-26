from __future__ import annotations

from typing import Dict

max_tries: Dict = {
    'open_oracle_ebusiness_suite': 3
}

urls: Dict = {
    'oracle': {
        'ebusiness': 'https://global-ebusiness.oraclecorp.com/OA_HTML/OA.jsp?OAFunc=OAHOMEPAGE',
        'ebusiness_no_query_parameters': 'https://global-ebusiness.oraclecorp.com/OA_HTML/OA.jsp',
        'single_sign_on': 'https://login.oracle.com/mysso/signon.jsp',
        'single_sign_on_hiccup': 'https://login.oracle.com/oam/server/sso/auth_cred_submit',
        'timecards_partial': 'https://global-ebusiness.oraclecorp.com/OA_HTML/OA.jsp?_rc=HXCTIMECARDACTIVITIESPAGE',
        'timecards_alt_partial': 'https://global-ebusiness.oraclecorp.com/OA_HTML/RF.jsp'
    }
}

timecard: Dict = {
    'html': {
        'table_tbody_xpath': "//span[@id='Hxctimecard']/table[2]//table[2]/tbody/tr[5]/td/table/tbody/tr[5]/td[2]/table/tbody"
    },
    # Project, Task, Type, Work_Location_Country, Work_Location_State_Province
    'num_cols_before_time': 5,
    'sleep_time': {
        'after_project_field': 1,  # in seconds
        'wait_for_data_entry': 1,  # in seconds
        'before_adding_html_row': 2,  # in seconds
        'after_adding_html_row': 2  # in seconds
    }
}
