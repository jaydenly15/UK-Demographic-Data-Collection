# Data Collection Handover

This README provides instructions and context for the datasets used in this project. It describes the available data sources, their formats, granularity, and how they are organized. Please read this carefully before continuing work.

---

## 1. Population Estimates (2011–2022)

**Description:**
Annual mid-year population estimates broken down by *gender, LSOA (2021 definitions), and single year of age* from 0 to 90.

**Granularity:**

- Geography: Lower Super Output Area (LSOA, 2021 boundaries)
- Time: Annual, 2011–2022
- Demographics: Male/Female, single-year age bands (0–90)

**Format:**
CSV files with the following columns:

```
Year, LAD 2021 Code, LAD 2021 Name, LSOA 2021 Code, LSOA 2021 Name, Total,
F0, F1, ..., F90, M0, M1, ..., M90
```

- `F0–F90`: Female population by age
- `M0–M90`: Male population by age
- `Total`: Sum across all age and gender groups

**Relative Paths:**

- `LSOA_Population_Estimates (csv)/sapelsoa_11to14.csv`
- `LSOA_Population_Estimates (csv)/sapelsoa_15to18.csv`
- `LSOA_Population_Estimates (csv)/sapelsoa_19to22.csv`

---

## 2. Death Numbers (2011–2022)

**Description:**
Annual death counts by *gender, LSOA (2021 definitions), and age groups*. Male and female deaths are stored in separate files.

**Granularity:**

- Geography: Lower Super Output Area (LSOA, 2021 boundaries)
- Time: Annual, 2011–2022
- Demographics: Male/Female, age bands (e.g., `<1`, `01–04`, `05–09`, …, `95+`)

**Format:**
CSV files with the following columns:

```
Year, LSOA21 Code, LSOA21 Name, <1, 01-04, 05-09, ..., 95+
```

**Relative Paths:**

- `LSOA_Death_Numbers (csv)/deathsbylsoa_female_01to23.csv`
- `LSOA_Death_Numbers (csv)/deathsbylsoa_male_01to23.csv`

---

## 3. Covariates

**Description:**
Additional socio-economic and demographic covariates at the LSOA level, sourced from:

- 2011 Census: Country of birth, Health and provision of unpaid care, Hours worked, Distance travelled to work, Hours worked, NS-SeC, Country of birth
- 2021 Census: Country of birth, Disability, Distance travelled to work, Hours worked, NS-SeC, Migrant Indicator
- Indices of Deprivation ([2010](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2010), [2015](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2015), [2019](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019) releases - see File 7 in hyperlinks)

More census covariates can be sourced using the tool `downloadCensusTable.ipynb`. More details below...

**Granularity:**

- **2011 Census** uses 2011 LSOA boundaries where as **2021 Census** uses 2021 LSOA boundaries. These can be mapped using the lookup on [Open Geography Portal](https://geoportal.statistics.gov.uk/search?sort=Date%20Created%7Ccreated%7Cdesc&tags=LUP_EXACT_LSOA11_LSOA21)
- The LSOA boundaries used for the **IMD dataset** has not been checked and should be further investigated. 

**Relative Paths:**

- `census_data_2011.csv`
- `census_data_2021.csv`
- `imd_scores_2010.csv`
- `imd_scores_2015.csv`
- `imd_scores_2019.csv`

---

## 4. Census Data – Data Ingestion

**Description:**
The ingestion process allows you to identify, download, clean, and merge Census datasets available at LSOA level for both 2011 and 2021.

**Files and Scripts:**

- `availableCensusDatasetsScraper.py` – Scrapes the Census 2011 and 2021 Data Finder websites to find datasets available at LSOA granularity. Outputs metadata CSVs: `datasets_lsoa_2011.csv` and `datasets_lsoa_2021.csv`.
- `downloadCensusTable.ipynb` – Automates downloading, cleaning and merging of selected datasets. Key features:
  - Uses fuzzy matching to search for datasets of interest.
  - Builds the correct NOMIS API URLs by checking if datasets support percentage measures and/or include rural/urban dimensions.
  - Downloads datasets and cleans column names to PascalCase, prefixed with dataset code.
  - Merges multiple datasets on `Geography` and `GeographyCode`.
  - Stores the final merged covariates in `census_data_2011.csv` and `census_data_2021.csv`.

**Usage Notes:**
While the details above provide context, in practice you will primarily work with the `downloadCensusTable.ipynb` notebook. The typical workflow is as follows:

1. **Browse datasets:** Use fuzzy search within the notebook to identify datasets containing covariates of interest. 
```python
# Example covariates of interest
interests = ['Hours worked', 'NS-SeC', 'Country of birth', 
            'Health', 'Disability', 'Distance travelled to work', 'Migrant']

datasets_2011 = browseDatasets(interests, availableDatasets_2011)
datasets_2011
```
2. **Select datasets:** Manually choose dataset IDs from the search results and store them as a list. 
```python
# Datasets of interest
dataset_ids_2011 = ['NM_611_1', 'NM_617_1', 'NM_625_1', 'NM_153_1', 'NM_559_1', 'NM_562_1', 'NM_933_1']

# View and confirm needed datasets
availableDatasets_2011[
    availableDatasets_2011['dataset_id'].isin(dataset_ids_2011)
]
```
3. **Download and clean:** Use the `NOMISDatasetManager` class to fetch the selected datasets. The class automatically:
   - Reads in the existing dataset if `file_path` exists, otherwise it creates a new dataset at that location. 
   - Builds the correct NOMIS API URLs 
   - Downloads the dataset.
   - Cleans column names into PascalCase and prefixes them with the dataset code.
   - Merges all selected datasets on LSOA to produce a single LSOA-level dataset. The merged dataset is saved to `file_path`.
   - You can also specify a `col_names_mapping_path` which stores the mapping between the cleaned and original column names, since the data cleaning changes the column names. 
```python
manager = NOMISDatasetManager()
manager.mergeDatasetsByCodes(
    dataset_ids_2011, 2011, file_path='census_data_2011.csv', col_names_mapping_path='column_names_census_2011'
)
```
**Additional Notes:** The method `NOMISDatasetManager.mergeDatasetsByCodes` can take an existing dataset via `file_path` and merge in new datasets. Any datasets already included in the existing file at `file_path` are automatically skipped to prevent duplication. The method can also build a new LSOA-level covariate dataset from scratch by passing in a non-existent `file_path`.

**Sources:**

- [Census 2011 Data Finder](https://www.nomisweb.co.uk/census/2011/data_finder)
- [Census 2021 Data Finder](https://www.nomisweb.co.uk/census/2021/data_finder)


