# vufind-dewey-cleaner
A Python utility for VuFind application users to clean slashes (/) from Dewey Decimal Classification numbers in Solr records

# Dewey Slash Cleaner

A Python-based utility to clean slashes (`/`) from Dewey Decimal Classification numbers in a Solr index. This tool identifies and removes all slashes in Dewey numbers stored in specified fields of the Solr documents.

## Features

- **Slash Removal**: Automatically removes all slashes (`/`) from Dewey Decimal Classification numbers in Solr records.
- **Batch Processing**: Processes large datasets in batches for efficiency.
- **Customizable Fields**: Supports multiple Dewey fields (e.g., `dewey-full`, `dewey-raw`, `dewey-search`).
- **Conversion Examples**: Includes examples to demonstrate the functionality.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/abidfakhrealam/vufind-dewey-cleaner.git
   cd vufind-dewey-cleaner

2. Install the required dependencies:
   ```bash
   pip install pysolr
   
3. Ensure your Solr instance is running and accessible.

## Usage

1. Update the Solr connection URL in the main() function:
   ```bash
   solr = pysolr.Solr('http://your-solr-host:8983/solr/biblio', always_commit=False)

2. Run the script:
   ```bash
   python script.py

3. Follow the prompts to review the number of affected records and confirm updates.

## Conversion Logic

The script removes all slashes (/) from Dewey numbers, regardless of their position.

## Examples:
| Input            | Output          |
| ---------------- | --------------- |
| `001.1/094/0903` | `001.10940903`  |
| `001.1/094`      | `001.1094`      |
| `001.0917/67`    | `001.091767`    |
| `001.09/02`      | `001.0902`      |
| `001.1/09409032` | `001.109409032` |


## Batch Processing
The script processes records in batches (default: 500 records per batch). You can modify the batch_size variable in the main() function to adjust the size.





