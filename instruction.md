# Objective

Allow a user to interact with a map of the united states by region (regions will be defined in a different section). Upon selecting a region, a user should be given the option to make a chloropleth map of population by county for that region (parameters for this will be included below).

## Tooling

This project should make use of python GUI libraries like tk or similar to create all UI features.

## Data and Defintions

 * source_geometries/counties.geojson
    - Type: File
    - Description: A geojson file containing county shapes and population data for each county
    - Example feature: {'attributes': {'OBJECTID': 1,
                        'NAME': 'Autauga County',
                        'STATE_NAME': 'Alabama',
                        'STATE_ABBR': 'AL',
                        'STATE_FIPS': '01',
                        'COUNTY_FIPS': '001',
                        'FIPS': '01001',
                        'POPULATION': 60428,
                        'POP_SQMI': 100,
                        'SQMI': 604.37,
                        'Shape_Length': 2.066026228699913,
                        'Shape_Area': 0.15025582494087603},
                        'geometry': {'rings': [[[-86.43963199999996, 32.70821300000006],
                            [-86.42442799999998, 32.70773800000006],
                            ...]]}}
    - Important Attribute Keys:
        + NAME
        + STATE_NAME
        + STATE_ABBR
        + STATE FIPS
        + COUNTY_FIPS
        + POPULATION

 * source_geometries/states.geojson
    - Type: File
    - Description: A geojson file containing state shapes in the USA
    - Example Feature: {'type': 'Feature',
                        'id': 1,
                        'geometry': {'type': 'Polygon',
                        'coordinates': [[[-94.29159710660633, 36.4992989891492],
                            [-94.31323910735283, 36.49937999105754],
                            ...]]},
                        'properties': {'FID': 1,
                        'OBJECTID': 1,
                        'NAME': 'Arkansas',
                        'STATE_ABBR': 'AR',
                        'STATE_FIPS': '05',
                        'ORDER_ADM': 25,
                        'MONTH_ADM': 'June',
                        'DAY_ADM': 15,
                        'YEAR_ADM': 1836,
                        'TYPE': 'Land',
                        'POP': 2915918,
                        'SQ_MILES': 53181.2,
                        'PRIM_MILES': 1329.6,
                        'Shape_Leng': 21.737081642,
                        'Shape__Area': 13.586154712604824,
                        'Shape__Length': 21.737081641968615}}
    - Important Propery Keys:
        +  NAME
        +  STATE_ABBR
        +  STATE_FIPS

 * USA Stats By Region
    - Definition
    - Regions
        + West
            - Washington
            - Montana
            - Idaho
            - Oregon
            - Whyoming
            - California
            - Nevada
            - Utah
            - Colorado
            - Alaska
            - Hawaii
        + Midwest
            - North Dakota
            - South Dakota
            - Nebraska
            - Kansas
            - Minnesota
            - Iowa
            - Missouri
            - Wisconsin
            - Illinois
            - Indiana
            - Michigan
            - Ohio
        + Northeast
            - Pensylvannia
            - Maralynd
            - Deleware
            - New Jersey
            - Conecticut
            - Rhode Island
            - Massechusets
            - New York
            - Vermont
            - New Hampshire
            - Maine
        + Southeast
            - Washington D.C.
            - Virginia
            - West Virginia
            - Kentucky
            - Arkansas
            - Louisiana
            - Mississippi
            - Alabama
            - Georgia
            - Florida
            - South Carolina
            - North Carolina
            - Tennessee
        + Southwest
            - Oklahoma
            - Texas
            - New Mexico
            - Arizona

## Application Initial State

The Application should load initially to revel a map of states symbolized with white outlines and a solid fill that varies based on their region. Each state should be labeld using the state abbreviation and each region should be labeled. The application should bear a title which reads "Austin Averill's Population By Region Viewer". There should be a button which reads "Create Chloro" that is initially deactivated. User's should be able to click on a region, which will activate the "Create Chloro" button and take them to a new application state where they will be given options to generate a chloro. The Map view should contain a north arrow and a scale bar. The user should not be able to zoom in on this map. Alaska and Hawaii should be displayed in frames as non-contiguous.

## Application Chloro Generator

This is the state of the application that is produced after a user selects a region and clicks "Create Chloro" in the intial state. This should initially load to a view of the counties of any state in this region with a black outline and no fill or label. The user should be able to zoom in and out on this, and each county should display a tooltip with the total population onhover. The map view should contain a north arrow and a dynamic scale bar that adjusts as the user zooms. The user should be presented with two drop-down menus to decide how the chloropleth symbology is applied. The first drop down should allow the user to select a method from the following to determine the breaks in the chloropleth: [Wuantile, Natural Breaks( Jenks), Equal Interval]. Regardless of the method, there will always be five classes for the chloropleth. The second drop down should allow the user to select from various color ramps to apply to the chloropleth map. Once a user has made selections in both drop downs, they should be able to click an "Apply" button that will render the symbology across the displayed counties. 

## Addtional Chloropleth Feature

After a user generates a chloropleth in the previously described steps, they should have an option to export the map frame to a .html file.

## Key Considerations

 * Loading Times
    - The geojson data in the source_geometries directory contains large files. These should be loaded in memory when the application is initialized to avoid long loading periods for the user.


