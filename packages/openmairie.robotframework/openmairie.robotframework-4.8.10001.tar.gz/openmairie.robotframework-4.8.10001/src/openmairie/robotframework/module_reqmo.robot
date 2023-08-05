*** Settings ***
Documentation  Module 'Reqmo'.

*** Keywords ***
Depuis l'écran principal du module 'Reqmo'
    [Tags]
    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_REQMO}
    Page Should Not Contain Errors


Click On Submit Button In Reqmo
    [Tags]
    Wait Until Keyword Succeeds     ${TIMEOUT}     ${RETRY_INTERVAL}    Click Element    css=#reqmo-form form div.formControls input
    Sleep    1
    Page Should Not Contain Errors


