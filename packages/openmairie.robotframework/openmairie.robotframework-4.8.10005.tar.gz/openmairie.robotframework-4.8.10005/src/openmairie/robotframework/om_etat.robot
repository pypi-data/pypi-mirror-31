*** Settings ***
Documentation     Actions spécifiques aux états

*** Keywords ***
Depuis le listing des états
    [Tags]  om_etat
    [Documentation]  Accède au listing des états.

    Go To Tab  om_etat


Depuis le tableau des états
    [Tags]  om_etat
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Depuis le listing des états`.

    Depuis le listing des états


Depuis le listing des états de la collectivité
    [Tags]  om_etat  om_collectivite
    [Documentation]  ...
    [Arguments]  ${collectivite_libelle}
    #
    Depuis le contexte de la collectivité  ${collectivite_libelle}
    #
    On clique sur l'onglet  om_etat  état


Depuis le contexte de l'état
    [Tags]  om_etat
    [Documentation]  Permet d'accéder au formulaire en consultation
    ...    d'une lettre-type.
    [Arguments]  ${id}=null  ${libelle}=null

    Depuis le listing des états
    # On recherche la lettre-type
    Run Keyword If    '${id}' != 'null'    Use Simple Search    id    ${id}    ELSE IF    '${libelle}' != 'null'    Use Simple Search    libellé    ${libelle}    ELSE    Fail
    # On clique sur la lettre-type
    Run Keyword If    '${id}' != 'null'    Click On Link    ${id}    ELSE IF    '${libelle}' != 'null'    Click On Link    ${libelle}    ELSE    Fail

Ajouter le état depuis le menu
    [Tags]  om_etat
    [Documentation]  Permet d'ajouter un état
    [Arguments]  ${id}  ${libelle}  ${titre}  ${corps}  ${sql}  ${actif}=null  ${collectivite}=null

    Depuis le listing des états
    # On clique sur l'icone d'ajout
    Click On Add Button
    # On remplit le formulaire
    Saisir l'état  ${id}  ${libelle}  ${titre}  ${corps}  ${sql}  ${actif}  ${collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.


Modifier l'état
    [Tags]  om_etat

    [Documentation]  Modifie l'enregistrement

    [Arguments]    ${om_etat}    ${om_collectivite}=null    ${id}=null    ${libelle}=null    ${actif}=null    ${orientation}=null    ${format}=null    ${logo}=null    ${logoleft}=null    ${logotop}=null    ${titre_om_htmletat}=null    ${titreleft}=null    ${titretop}=null    ${titrelargeur}=null    ${titrehauteur}=null    ${titrebordure}=null    ${corps_om_htmletatex}=null    ${om_sql}=null    ${se_font}=null    ${se_couleurtexte}=null    ${margeleft}=null    ${margetop}=null    ${margeright}=null    ${margebottom}=null

    # On accède à l'enregistrement
    Depuis le contexte de l'état    ${om_etat}
    # On clique sur le bouton modifier
    Click On Form Portlet Action    om_etat    modifier
    # On saisit des valeurs
    Saisir l'état    ${om_collectivite}    ${id}    ${libelle}    ${actif}    ${orientation}    ${format}    ${logo}    ${logoleft}    ${logotop}    ${titre_om_htmletat}    ${titreleft}    ${titretop}    ${titrelargeur}    ${titrehauteur}    ${titrebordure}    ${corps_om_htmletatex}    ${om_sql}    ${se_font}    ${se_couleurtexte}    ${margeleft}    ${margetop}    ${margeright}    ${margebottom}
    # On valide le formulaire
    Click On Submit Button


Saisir l'état
    [Tags]  om_etat

    [Documentation]  Permet de remplir le formulaire d'un état

    [Arguments]  ${id}  ${libelle}  ${titre}  ${corps}  ${sql}  ${actif}  ${collectivite}

    # On saisit l'id
    Run Keyword If  '${id}' != 'null'  Input Text  id  ${id}
    # On saisit le libellé
    Run Keyword If  '${libelle}' != 'null'  Input Text  libelle  ${libelle}
    # On saisit le titre
    Run Keyword If  '${titre}' != 'null'  Input HTML  titre_om_htmletat  ${titre}
    # On saisit le corps
    Run Keyword If  '${corps}' != 'null'  Input HTML  corps_om_htmletatex  ${corps}
    # On sélectionne la requête
    Run Keyword If  '${sql}' != 'null'  Select From List By Label  om_sql  ${sql}
    # On coche actif si spécifié
    Run Keyword If  '${actif}' == 'true'  Select Checkbox  actif
    # On décoche actif si spécifié
    Run Keyword If  '${actif}' == 'false'  Unselect Checkbox  actif
    # On sélectionne la collectivité
    Run Keyword If  '${collectivite}' != 'null'  Select From List By Label  om_collectivite  ${collectivite}
