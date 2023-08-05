*** Settings ***
Documentation     Actions navigation

*** Keywords ***
Depuis la page d'accueil
    [Tags]
    [Arguments]  ${username}  ${password}
    [Documentation]    L'objet de ce 'Keyword' est de positionner l'utilisateur
    ...    sur la page de login ou son tableau de bord si on le fait se connecter.

    # On accède à la page d'accueil
    Go To  ${PROJECT_URL}
    Page Should Not Contain Errors

    # On vérifie si un utilisateur est connecté ou non
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Be Visible  css=#title h2
    ${titre} =  Get Text  css=#title h2
    ${is_connected} =  Evaluate  "${titre}"!="Veuillez Vous Connecter"

    # On récupère le login de l'utilisateur si un utilisateur est connecté
    ${connected_login} =  Set Variable  None
    ${connected_login} =  Run Keyword If  "${is_connected}"=="True"  Get Text  css=#actions li.action-login

    # L'utilisateur souhaité est déjà connecté, on sort
    Run Keyword If  "${connected_login}"=="${username}"  Return From Keyword  L'utilisateur souhaité est déjà connecté.

    # On se déconnecte si un utilisateur est déjà connecté
    Run Keyword If  "${is_connected}"=="True"  Click Link  css=#actions a.actions-logout

    # On vérifie si l'utilisateur est connecté ou non
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Be Visible  css=#title h2
    ${titre} =  Get Text  css=#title h2
    ${is_connected} =  Evaluate  "${titre}"!="Veuillez Vous Connecter"

    # On s'authentifie avec le nouvel utilisateur
    S'authentifier  ${username}  ${password}


Go To Login Page
    [Tags]
    Go To    ${PROJECT_URL}
    Wait Until Element Is Visible    css=#title h2
    Element Text Should Be    css=#title h2    Veuillez Vous Connecter
    Title Should Be    ${TITLE}
    Page Should Not Contain Errors

Go To Dashboard
    [Tags]
    Click Link    css=#logo h1 a.logo
    Page Title Should Be    Tableau De Bord
    Page Should Not Contain Errors

Go To Tab
    [Tags]
    [Arguments]    ${obj}
    Go To    ${PROJECT_URL}${OM_ROUTE_TAB}&obj=${obj}
    Wait Until Keyword Succeeds     ${TIMEOUT}     ${RETRY_INTERVAL}    Page Should Not Contain Errors

S'authentifier
    [Tags]
    [Arguments]    ${username}=${ADMIN_USER}    ${password}=${ADMIN_PASSWORD}
    Input Username    ${username}
    Input Password    ${password}
    #
    Click Element    login.action.connect
    #
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain    css=#actions a.actions-logout    Déconnexion
    #
    Page Should Not Contain Errors

Se déconnecter
    [Tags]
    Wait Until Element Is Visible    css=#title h2
    Element Text Should Be    css=#title h2    Tableau De Bord
    Click Link    css=#actions a.actions-logout
    Wait Until Element Is Visible    css=#title h2
    Element Text Should Be    css=#title h2    Veuillez Vous Connecter
    Page Should Not Contain Errors

Reconnexion
    [Tags]
    [Arguments]    ${username}=null    ${password}=null
    ${connected_login} =    Get Text    css=#actions ul.actions-list li.action-login
    # On se déconnecte si user logué différent
    Run Keyword If   '${username}' != '${connected_login}'    Se déconnecter
    # On se reconnecte si user spécifié et différent du logué
    Run Keyword If   '${username}' != 'null' and '${password}' != 'null' and '${username}' != '${connected_login}'    S'authentifier    ${username}    ${password}

Ouvrir le navigateur
    [Tags]
    [Arguments]    ${width}=1024    ${height}=768
    Open Browser    ${PROJECT_URL}    ${BROWSER}
    Set Window Size    ${width}    ${height}
    Set Selenium Speed    ${DELAY}
    Wait Until Element Is Visible    css=#title h2
    Element Text Should Be    css=#title h2    Veuillez Vous Connecter
    Title Should Be    ${TITLE}

Ouvrir le navigateur et s'authentifier
    [Tags]
    [Arguments]    ${username}=${ADMIN_USER}    ${password}=${ADMIN_PASSWORD}
    Ouvrir le navigateur
    S'authentifier    ${username}    ${password}

Fermer le navigateur
    [Tags]
    Close Browser

Page Title Should Be
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Element Is Visible    css=#title h2
    Element Text Should Be    css=#title h2    ${messagetext}

Page Title Should Contain
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Element Is Visible    css=#title h2
    Element Should Contain    css=#title h2    ${messagetext}

Page SubTitle Should Contain
    [Tags]
    [Arguments]    ${subcontainer_id}    ${messagetext}
    Wait Until Element Is Visible    css=#${subcontainer_id} div.subtitle h3
    Element Should Contain    css=#${subcontainer_id} div.subtitle h3    ${messagetext}

Page SubTitle Should Be
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Element Is Visible    css=div.subtitle h3
    Element Text Should Be    css=div.subtitle h3    ${messagetext}

Page Should Not Contain Errors
    [Tags]
    Page Should Not Contain    Erreur de base de données.
    Page Should Not Contain    Fatal error
    Page Should Not Contain    Parse error
    Page Should Not Contain    Notice
    Page Should Not Contain    Warning


L'onglet doit être présent
    [Tags]
    [Documentation]
    [Arguments]    ${id}=null    ${libelle}=null

    #
    ${locator} =    Catenate    SEPARATOR=    css=#formulaire ul.ui-tabs-nav li a#    ${id}
    #
    Element Text Should Be    ${locator}    ${libelle}


L'onglet doit être sélectionné
    [Tags]
    [Documentation]
    [Arguments]    ${id}=null    ${libelle}=null

    #
    ${locator} =    Catenate    SEPARATOR=    css=#formulaire ul.ui-tabs-nav li.ui-tabs-selected a#    ${id}
    #
    Element Text Should Be    ${locator}    ${libelle}


On clique sur l'onglet
    [Tags]
    [Documentation]
    [Arguments]    ${id}=null    ${libelle}=null

    #
    ${locator} =    Catenate    SEPARATOR=    css=#formulaire ul.ui-tabs-nav li a#    ${id}
    #
    L'onglet doit être présent    ${id}    ${libelle}
    #
    Click Element    ${locator}
    #
    L'onglet doit être sélectionné    ${id}    ${libelle}
    #
    Sleep    1
    #
    Page Should Not Contain Errors


Sélectionner la fenêtre et vérifier l'URL puis fermer la fenêtre
    [Tags]

    [Documentation]  Permet de vérifier que la nouvelle fenêtre de Firefox qui a pour
    ...  titre ${identifiant_fenetre} pointe bien sur ${URL}.
    ...  Si ${correspondance_exacte} vaut false alors ${URL} est une liste et on vérifie
    ...  que l'url en contient chaque élément.

    [Arguments]  ${identifiant_fenetre}  ${URL}  ${correspondance_exacte}=true

    # Sélection de la nouvelle fenêtre
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Select Window  ${identifiant_fenetre}
    Run Keyword If  '${correspondance_exacte}' == 'true'   Location Should Be  ${URL}
    Run Keyword If  '${correspondance_exacte}' == 'false'  L'URL doit contenir  ${URL}
    # Fermeture de la nouvelle fenêtre
    Close Window
    # Sélection de la fenêtre courante
    Select Window

L'URL doit contenir
    [Arguments]    ${text_list}
    [Documentation]  Permet de vérifier ce que contient l'URL

    :FOR  ${text}  IN  @{text_list}
    \    Location Should Contain  ${text}


L'onglet ne doit pas être présent
    [Documentation]  Vérifie que l'onglet n'est pas affiché.
    [Arguments]  ${id}=null

    ${locator} =  Catenate  SEPARATOR=  css=#formulaire ul.ui-tabs-nav li a#  ${id}
    Element Should Not Be Visible  ${locator}
