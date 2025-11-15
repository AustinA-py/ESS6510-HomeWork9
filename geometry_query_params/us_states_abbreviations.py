"""
US States and Abbreviations Dictionary

A comprehensive dictionary mapping US state names to their standard postal abbreviations.
Includes all 50 states, District of Columbia, and major territories.
"""

US_STATES_ABBREVIATIONS = {
    # States (alphabetical order)
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
    
    # Federal District
    'District of Columbia': 'DC',
    
    # Major Territories
    'Puerto Rico': 'PR',
    'U.S. Virgin Islands': 'VI',
    'Guam': 'GU',
    'American Samoa': 'AS',
    'Northern Mariana Islands': 'MP'
}

# Reverse mapping (abbreviation to state name)
US_ABBREVIATIONS_STATES = {v: k for k, v in US_STATES_ABBREVIATIONS.items()}

def get_state_abbreviation(state_name: str) -> str:
    """
    Get the abbreviation for a given state name.
    
    Args:
        state_name: Full state name
        
    Returns:
        State abbreviation or empty string if not found
    """
    return US_STATES_ABBREVIATIONS.get(state_name, '')

def get_state_name(abbreviation: str) -> str:
    """
    Get the full state name for a given abbreviation.
    
    Args:
        abbreviation: State abbreviation (2 letters)
        
    Returns:
        Full state name or empty string if not found
    """
    return US_ABBREVIATIONS_STATES.get(abbreviation.upper(), '')

def is_valid_state(state_name: str) -> bool:
    """
    Check if a given state name is valid.
    
    Args:
        state_name: State name to validate
        
    Returns:
        True if valid state name, False otherwise
    """
    return state_name in US_STATES_ABBREVIATIONS

def is_valid_abbreviation(abbreviation: str) -> bool:
    """
    Check if a given abbreviation is valid.
    
    Args:
        abbreviation: State abbreviation to validate
        
    Returns:
        True if valid abbreviation, False otherwise
    """
    return abbreviation.upper() in US_ABBREVIATIONS_STATES

if __name__ == "__main__":
    # Example usage and testing
    print("US States and Abbreviations Dictionary")
    print("=" * 40)
    
    # Print all states and abbreviations
    for state, abbr in sorted(US_STATES_ABBREVIATIONS.items()):
        print(f"{state:<25} -> {abbr}")
    
    print(f"\nTotal entries: {len(US_STATES_ABBREVIATIONS)}")
    
    # Test functions
    print("\nFunction Tests:")
    print(f"California abbreviation: {get_state_abbreviation('California')}")
    print(f"TX full name: {get_state_name('TX')}")
    print(f"Is 'Florida' valid? {is_valid_state('Florida')}")
    print(f"Is 'XY' valid abbreviation? {is_valid_abbreviation('XY')}")