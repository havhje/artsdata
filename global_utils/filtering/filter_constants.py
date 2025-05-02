##### Constants #####
# Define codes/labels/mappings used in status filters

REDLIST_CODES = ['CR', 'EN', 'VU', 'NT', 'LC', 'DD', 'NE'] # Codes representing Red List categories. Higher codes indicate greater risk.
ALIEN_CODES = ['SE', 'HI', 'PH', 'LO'] # Codes representing Alien Species risk categories. Higher codes indicate greater ecological impact.
SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL = {
    "Prioriterte Arter": "Prioriterte arter", # Maps display label to original DataFrame column name for Prioriterte Arter.
    "Andre Spes. Hensyn": "Andre spesielt hensynskrevende arter", # Maps display label to original DataFrame column name for Andre Spesielt Hensynskrevende Arter.
    "Ansvarsarter": "Ansvarsarter", # Maps display label to original DataFrame column name for Ansvarsarter.
    "Spes. Økol. Former": "Spesielle okologiske former", # Maps display label to original DataFrame column name for Spesielle Økologiske Former.
    "Truede Arter": "Trua arter", # Maps display label to original DataFrame column name for Truede Arter.
    "Fredete Arter": "Fredete arter" # Maps display label to original DataFrame column name for Fredete Arter.
} 