*** Settings ***
Documentation  Module 'Import'.

*** Keywords ***
Depuis l'écran principal du module 'Import'
    [Tags]
    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_IMPORT}
    Page Should Not Contain Errors


Depuis l'import
    [Tags]
    [Arguments]  ${obj}
    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_IMPORT}&obj=${obj}
    Page Should Not Contain Errors


Click On Submit Button In Import CSV
    [Tags]
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Click Element  css=#form-csv-import form div.formControls input
    Sleep  1
    Page Should Not Contain Errors


