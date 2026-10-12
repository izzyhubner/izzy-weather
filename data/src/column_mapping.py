
COLUMN_MAPPING = {
    # Identifiers and dates
    "Protocolo_S2iD": "disaster_id",
    "Data_Registro": "registration_date",
    "Data_Evento": "event_date",
    "Cod_IBGE_Mun": "municipality_code",
    "Cod_Cobrade": "cobrade_code",

    # Geography
    "Nome_Municipio": "municipality_name",
    "Sigla_UF": "state_code",
    "regiao": "region",

    # Disaster classification
    "grupo_de_desastre": "disaster_group",
    "tipologia": "disaster_type_code",
    "descricao_tipologia": "disaster_type_description",

    # Human impacts
    "DH_MORTOS": "deaths",
    "DH_FERIDOS": "injured_people",
    "DH_ENFERMOS": "ill_people",
    "DH_DESABRIGADOS": "sheltered_people",
    "DH_DESALOJADOS": "displaced_people",
    "DH_DESAPARECIDOS": "missing_people",
    "DH_AFETADOS_SECA_ESTIAGEM": "drought_affected_people",
    "DH_total_danos_humanos_diretos": "total_directly_affected_people",
    "DH_OUTROS AFETADOS": "other_affected_people",

    # Material damage: housing
    "DM_Uni Habita Danificadas": "damaged_housing_units",
    "DM_Uni Habita Destruidas": "destroyed_housing_units",
    "DM_Uni Habita Valor": "housing_damage_value_brl",

    # Material damage: health facilities
    "DM_Inst Saúde Danificadas": "damaged_health_facilities",
    "DM_Inst Saúde Destruidas": "destroyed_health_facilities",
    "DM_Inst Saúde Valor": "health_facilities_damage_value_brl",

    # Material damage: educational facilities
    "DM_Inst Ensino Danificadas": "damaged_educational_facilities",
    "DM_Inst Ensino Destruidas": "destroyed_educational_facilities",
    "DM_Inst Ensino Valor": "educational_facilities_damage_value_brl",

    # Material damage: service facilities
    "DM_Inst Serviços Danificadas": "damaged_service_facilities",
    "DM_Inst Serviços Destruidas": "destroyed_service_facilities",
    "DM_Inst Serviços Valor": "service_facilities_damage_value_brl",

    # Material damage: communication facilities
    "DM_Inst Comuni Danificadas": "damaged_communication_facilities",
    "DM_Inst Comuni Destruidas": "destroyed_communication_facilities",
    "DM_Inst Comuni Valor": "communication_facilities_damage_value_brl",

    # Material damage: infrastructure
    "DM_Obras de Infra Danificadas": "damaged_infrastructure_works",
    "DM_Obras de Infra Destruidas": "destroyed_infrastructure_works",
    "DM_Obras de Infra Valor": "infrastructure_damage_value_brl",

    # Total material damage
    "DM_total_danos_materiais": "total_material_damage_brl",

    # Public economic losses
    "PEPL_Assis_méd e emergên(R$)": "public_health_emergency_losses_brl",
    "PEPL_Abast de água pot(R$)": "public_water_supply_losses_brl",
    "PEPL_sist de esgotos sanit(R$)": "public_sewage_system_losses_brl",
    "PEPL_Sis limp e rec lixo (R$)": "public_waste_management_losses_brl",
    "PEPL_Sis cont pragas (R$)": "public_pest_control_losses_brl",
    "PEPL_distrib energia (R$)": "public_energy_distribution_losses_brl",
    "PEPL_Telecomunicações (R$)": "public_telecommunications_losses_brl",
    "PEPL_Tran loc/reg/l_curso (R$)": "public_local_regional_transport_losses_brl",
    "PEPL_Distrib combustíveis(R$)": "public_fuel_distribution_losses_brl",
    "PEPL_Segurança pública (R$)": "public_public_safety_losses_brl",
    "PEPL_Ensino (R$)": "public_education_losses_brl",
    "PEPL_total_publico": "total_public_losses_brl",

    # Private economic losses
    "PEPR_Agricultura (R$)": "private_agriculture_losses_brl",
    "PEPR_Pecuária (R$)": "private_livestock_losses_brl",
    "PEPR_Indústria (R$)": "private_industry_losses_brl",
    "PEPR_Comércio (R$)": "private_commerce_losses_brl",
    "PEPR_Serviços (R$)": "private_services_losses_brl",
    "PEPR_total_privado": "total_private_losses_brl",

    # Combined economic losses
    "PE_PLePR": "total_public_private_losses_brl",

    
    # Environmental impacts
    "DA_Polui/cont da água": "water_pollution",
    "DA_Polui/cont do ar": "air_pollution",
    "DA_Polui/cont do solo": "soil_pollution",
    "DA_Dimi/exauri hídrico": "water_resource_depletion",
    "DA_Incêndi parques/APA's/APP's": "protected_areas_fires",
}
