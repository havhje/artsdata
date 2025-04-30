"""Maps technical column names to user-friendly display names."""

COLUMN_NAME_MAPPING = {
    # Core Identification & Biology
    "scientificName": "Vitenskapelig Navn",
    "validScientificName": "Vitenskapelig Navn",
    "validScientificNameId": "Arts ID - Artsdatabanken",
    "vernacularName": "Norsk Navn",
    "preferredPopularName": "Art",
    "taxonGroupName": "Taksonomisk Gruppe",
    "scientificNameRank": "Vitenskapelig Navn Rang",
    "sex": "Kjønn",
    "individualCount": "Antall Individer",
    "behavior": "Atferd",
    "taxonRemarks": "Taksonomiske Merknader",
    "Kingdom": "Rike",
    "Phylum": "Rekke",
    "Class": "Klasse",
    "Order": "Orden (Vitenskapelig)",
    "Family": "Familie (Vitenskapelig)",
    "Genus": "Slekt",
    "FamilieNavn": "Familie",
    "OrdenNavn": "Orden",

    # Event & Recording
    "eventDate": "Dato", #Ikke bruk
    "dateTimeCollected": "Innsamlingsdato/-tid",
    "recordedBy": "Registrert Av",
    "collector": "Innsamler/Observatør",
    "basisOfRecord": "Basis for Registrering",
    "notes": "Merknader",

    # Location
    "county": "Fylke",
    "municipality": "Kommune",
    "locality": "Lokalitet",
    "decimalLatitude": "Desimalbreddegrad",
    "decimalLongitude": "Desimallengdegrad",
    "latitude": "Breddegrad",
    "longitude": "Lengdegrad",
    "lat": "Breddegrad",
    "lon": "Lengdegrad",
    "coordinateUncertaintyInMeters": "Koordinat Usikkerhet (meter)",
    "geometry": "Geometri",

    # Collection & Identification Details
    "institutionCode": "Institusjonskode",
    "collectionCode": "Samlingskode",
    "catalogNumber": "Katalognummer",
    "occurrenceID": "Occurrence ID",
    "recordNumber": "Record Number",

    # Conservation & Management
    "category": "Kategori (Rødliste/Fremmedart)",
    "Prioriterte arter": "Prioriterte Arter",
    "Andre spesielt hensynskrevende arter": "Andre Spes. Hensyn.",
    "Ansvarsarter": "Ansvarsarter",
    "Spesielle okologiske former": "Spes. Økol. Former",
    "Fremmede arter": "Fremmede arter kategori",
    "Trua arter": "Truede Arter",
    "Fredete arter": "Fredete Arter",
    "NT": "Nær Truet (NT)",

    # Add other columns from your specific dataset if needed
}


def get_display_name(original_name: str) -> str:
    """Return display name for a column, fallback to original if no mapping."""
    return COLUMN_NAME_MAPPING.get(original_name, original_name)
