*** Settings ***
Documentation  Actions spécifiques aux collectivités.

*** Keywords ***
Depuis le tableau des collectivités
    [Tags]
    [Documentation]  Permet d'accéder au tableau des collectivités.

    # On ouvre le tableau
    Go To Tab  om_collectivite


Depuis le contexte de la collectivité
    [Tags]
    [Documentation]  Permet d'accéder au formulaire en consultation
    ...    d'une collectivité.
    [Arguments]  ${libelle}=null  ${om_collectivite}=null

    # On ouvre le tableau des collectivités
    Depuis le tableau des collectivités
    # On recherche la collectivité
    Run Keyword If    '${om_collectivite}' != 'null'    Use Simple Search    Collectivité    ${om_collectivite}    ELSE IF    '${libelle}' != 'null'    Use Simple Search    libellé    ${libelle}    ELSE    Fail
    # On clique sur la collectivité
    Run Keyword If    '${om_collectivite}' != 'null'    Click On Link    ${om_collectivite}    ELSE IF    '${libelle}' != 'null'    Click On Link    ${libelle}    ELSE    Fail


Ajouter la collectivité depuis le menu
    [Tags]
    [Documentation]  Permet d'ajouter un droit depuis le formulaire collectivité.
    [Arguments]  ${libelle}  ${niveau}

    # On ouvre le tableau des collectivités
    Depuis le tableau des collectivités
    # On clique sur l'icone d'ajout
    Click On Add Button
    # On remplit le formulaire
    Saisir la collectivité  ${libelle}  ${niveau}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.

Saisir la collectivité
    [Tags]
    [Documentation]  Permet de remplir le formulaire d'une collectivité.
    [Arguments]  ${libelle}  ${niveau}

    # On saisit le libellé
    Input Text  libelle  ${libelle}
    # On sélectionne le niveau
    Select From List By Label  niveau  ${niveau}
