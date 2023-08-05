*** Settings ***
Documentation  Actions spécifiques aux utilisateurs.

*** Keywords ***
Depuis le tableau des utilisateurs
    [Tags]
    [Documentation]  Permet d'accéder au tableau des utilisateurs.

    # On ouvre le tableau
    Go To Tab  om_utilisateur

Depuis le contexte de l'utilisateur
    [Tags]
    [Documentation]  Permet d'accéder au formulaire en consultation
    ...    d'un utilisateur.
    [Arguments]  ${login}=null  ${email}=null

    # On ouvre le tableau des utilisateurs
    Depuis le tableau des utilisateurs
    # On recherche l'utilisateur
    Run Keyword If    '${login}' != 'null'    Use Simple Search    login    ${login}    ELSE IF    '${email}' != 'null'    Use Simple Search    email    ${email}    ELSE    Fail
    # On clique sur l'utilisateur
    Run Keyword If    '${login}' != 'null'    Click On Link    ${login}    ELSE IF    '${email}' != 'null'    Click On Link    ${email}    ELSE    Fail

Ajouter l'utilisateur
    [Tags]
    [Documentation]  Permet d'ajouter un utilisateur en accédant directement au formulaire
    [Arguments]  ${nom}  ${email}  ${login}  ${password}  ${profil}  ${collectivite}=null

    Go To  ${PROJECT_URL}${OM_ROUTE_FORM}&obj=om_utilisateur&action=0
    # On remplit le formulaire
    Saisir l'utilisateur  ${nom}  ${email}  ${login}  ${password}  ${profil}  ${collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.

Ajouter l'utilisateur depuis le menu
    [Tags]
    [Documentation]  Permet d'ajouter un utilisateur en passant par le menu
    [Arguments]  ${nom}  ${email}  ${login}  ${password}  ${profil}  ${collectivite}=null

    # On ouvre le tableau des utilisateurs
    Depuis le tableau des utilisateurs
    # On clique sur l'icone d'ajout
    Click On Add Button
    # On remplit le formulaire
    Saisir l'utilisateur  ${nom}  ${email}  ${login}  ${password}  ${profil}  ${collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.

Modifier l'utilisateur
    [Tags]
    [Documentation]  Permet de modifier un utilisateur en passant par le menu
    [Arguments]  ${nom}  ${email}  ${login}  ${password}  ${profil}  ${collectivite}=null

    Depuis le contexte de l'utilisateur  ${login}  ${email}
    # On clique sur l'icone d'ajout
    Click On Form Portlet Action  om_utilisateur  modifier
    # On remplit le formulaire
    Saisir l'utilisateur  ${nom}  ${email}  null  ${password}  ${profil}  ${collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.


Saisir l'utilisateur
    [Tags]
    [Documentation]  Permet de remplir le formulaire d'un utilisateur.
    [Arguments]  ${nom}=null  ${email}=null  ${login}=null  ${password}=null  ${profil}=null  ${collectivite}=null

    # On saisit le nom
    Run Keyword If  '${nom}' != 'null'  Input Text  nom  ${nom}
    # On saisit l'email
    Run Keyword If  '${email}' != 'null'  Input Text  email  ${email}
    # On saisit le login
    Run Keyword If  '${login}' != 'null'  Input Text  login  ${login}
    # On saisit le mot de passe
    Run Keyword If  '${password}' != 'null'  Input Text  pwd  ${password}
    # On sélectionne la collectivité
    Run Keyword If  '${collectivite}' != 'null'  Select From List By Label  om_collectivite  ${collectivite}
     # On sélectionne le profil
    Run Keyword If  '${profil}' != 'null'  Select From List By Label  om_profil  ${profil}

Supprimer l'utilisateur
    [Tags]
    [Documentation]  Supprime l'enregistrement
    [Arguments]    ${utilisateur}

    # On accède à l'enregistrement
    Depuis le contexte de l'utilisateur    ${utilisateur}
    # On clique sur le bouton supprimer
    Click On Form Portlet Action    om_utilisateur    supprimer
    # On valide le formulaire
    Click On Submit Button
