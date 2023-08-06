*** Settings ***
Documentation  Module 'SIG interne'.

*** Keywords ***
Activer l'option 'SIG interne'
    [Tags]  module_sig_interne
    [Documentation]  Active l'option 'SIG interne'.
    Ajouter le paramètre depuis le menu  option_localisation  sig_interne  null


Désactiver l'option 'SIG interne'
    [Tags]  module_sig_interne
    [Documentation]  Désactive l'option 'SIG interne'.
    Supprimer le paramètre  option_localisation  sig_interne


Depuis le listing des étendues
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Accède au listing des étendues.
    Go To Tab  om_sig_extent


Depuis le contexte de l'étendue
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Accède à la fiche de consultation de l'étendue.
    [Arguments]  ${om_sig_extent}

    Depuis le listing des étendues
    # On recherche l'enregistrement
    Use Simple Search  om_sig_extent  ${om_sig_extent}
    # On clique sur le résultat
    Click On Link  ${om_sig_extent}
    # On vérifie qu'il n'y a pas d'erreur
    Page Should Not Contain Errors


Ajouter l'étendue
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Crée l'enregistrement
    [Arguments]  ${values}
    Depuis le listing des étendues
    # On clique sur le bouton ajouter
    Click On Add Button
    # On saisit des valeurs
    Saisir l'étendue  ${values}
    # On valide le formulaire
    Click On Submit Button
    Valid Message Should Be  Vos modifications ont bien été enregistrées.


Modifier l'étendue
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Modifie l'enregistrement
    [Arguments]  ${om_sig_extent}  ${values}
    # On accède à l'enregistrement
    Depuis le contexte de l'étendue  ${om_sig_extent}
    # On clique sur le bouton modifier
    Click On Form Portlet Action  om_sig_extent  modifier
    # On saisit des valeurs
    Saisir l'étendue  ${values}
    # On valide le formulaire
    Click On Submit Button
    Valid Message Should Be  Vos modifications ont bien été enregistrées.


Supprimer l'étendue
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Supprime l'enregistrement
    [Arguments]  ${om_sig_extent}
    # On accède à l'enregistrement
    Depuis le contexte de l'étendue  ${om_sig_extent}
    # On clique sur le bouton supprimer
    Click On Form Portlet Action  om_sig_extent  supprimer
    # On valide le formulaire
    Click On Submit Button


Saisir l'étendue
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Remplit le formulaire
    [Arguments]  ${values}
    Si "nom" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "extent" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "valide" existe dans "${values}" on execute "Set Checkbox" dans le formulaire


Depuis le listing des flux
    [Tags]  om_sig_flux  module_sig_interne
    [Documentation]  Accède au listing des flux.
    Go To Tab  om_sig_flux


Ajouter le flux
    [Tags]  om_sig_flux  module_sig_interne
    [Documentation]  Crée l'enregistrement
    [Arguments]  ${values}
    Depuis le listing des flux
    # On clique sur le bouton ajouter
    Click On Add Button
    # On saisit des valeurs
    Saisir le flux  ${values}
    # On valide le formulaire
    Click On Submit Button
    Valid Message Should Be  Vos modifications ont bien été enregistrées.


Saisir le flux
    [Tags]  om_sig_flux  module_sig_interne
    [Documentation]  Remplit le formulaire
    [Arguments]  ${values}
    Si "libelle" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "om_collectivite" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "id" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "attribution" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "chemin" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "couches" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "cache_type" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "cache_gfi_chemin" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "cache_gfi_couches" existe dans "${values}" on execute "Input Text" dans le formulaire

Depuis le listing des cartes
    [Tags]  om_sig_map  module_sig_interne
    [Documentation]  Accède au listing des cartes.
    Go To Tab  om_sig_map

Ajouter la carte
    [Tags]  om_sig_map  module_sig_interne
    [Documentation]  Crée l'enregistrement
    [Arguments]  ${values}
    Depuis le listing des cartes
    # On clique sur le bouton ajouter
    Click On Add Button
    # On saisit des valeurs
    Saisir la carte  ${values}
    # On valide le formulaire
    Click On Submit Button
    Valid Message Should Be  Vos modifications ont bien été enregistrées.


Saisir la carte
    [Tags]  om_sig_map  module_sig_interne
    [Documentation]  Remplit le formulaire
    [Arguments]  ${values}
    Si "om_collectivite" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "id" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "libelle" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "actif" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "zoom" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "fond_osm" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "fond_bing" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "fond_sat" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "layer_info" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "projection_externe" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "url" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "om_sql" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "retour" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "util_idx" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "util_reqmo" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "util_recherche" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "source_flux" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "fond_default" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "om_sig_extent" existe dans "${values}" on sélectionne la valeur sur l'autocomplete "om_sig_extent" dans le formulaire
    Si "restrict_extent" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "sld_marqueur" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "sld_data" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "point_centrage" existe dans "${values}" on execute "Input Text" dans le formulaire

