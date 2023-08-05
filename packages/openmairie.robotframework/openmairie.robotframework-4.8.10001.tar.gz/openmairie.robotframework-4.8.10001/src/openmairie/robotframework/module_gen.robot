*** Settings ***
Documentation  Module 'Gen'.

*** Keywords ***
Depuis le module de génération
    [Tags]
    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_GEN}
    Page Should Not Contain Errors


Depuis l'assistant "Création d'état"
    [Tags]
    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_GEN}&view=editions_etat
    Page Should Not Contain Errors


Depuis l'assistant "Création de lettre type"
    [Tags]
    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_GEN}&view=editions_lettretype
    Page Should Not Contain Errors


Depuis l'assistant "Création de sous-état"
    [Tags]
    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_GEN}&view=editions_sousetat
    Page Should Not Contain Errors


Depuis l'assistant "Migration état, sous-état, lettre type"
    [Tags]
    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_GEN}&view=editions_old
    Page Should Not Contain Errors


Générer tout
    [Tags]
    Depuis le module de génération
    Click Element  css=#gen-action-gen-all
    Page Should Not Contain    Erreur de droits d'écriture
    Page Should Not Contain    Génération de
