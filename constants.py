urls = {
    'oracle': {
        'ebusiness': 'https://global-ebusiness.oraclecorp.com/OA_HTML/OA.jsp?OAFunc=OAHOMEPAGE',
        'ebusiness_no_query_parameters': 'https://global-ebusiness.oraclecorp.com/OA_HTML/OA.jsp',
        'single_sign_on': 'https://login.oracle.com/mysso/signon.jsp',
        'single_sign_on_hiccup': 'https://login.oracle.com/oam/server/sso/auth_cred_submit',
        'timecards_partial': 'https://global-ebusiness.oraclecorp.com/OA_HTML/OA.jsp?_rc=HXCTIMECARDACTIVITIESPAGE',
        'timecards_alt_partial': 'https://global-ebusiness.oraclecorp.com/OA_HTML/RF.jsp'
    }
}

COLS_BEFORE_TIME = 5  # Project, Task, Type, Work_Location_Country, Work_Location_State_Province
NUMBER_OF_ROWS_BEFORE_ADD = 6  # The number of HTML rows available to fill with timecard information before needing to add more rows.
