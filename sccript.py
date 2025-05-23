import pysolr
import re

def count_slash_records(solr):
    """Count records with / in Dewey numbers"""
    query = 'dewey-full:*/* OR dewey-raw:*/* OR dewey-search:*/*'
    return solr.search(query, rows=0).hits

def convert_dewey_format(dewey_str):
    """Remove all slashes (/) from the Dewey number."""
    if not isinstance(dewey_str, str):
        return dewey_str
    return dewey_str.replace('/', '')


def show_conversion_examples():
    """Show before/after examples of the conversion"""
    examples = [
        ("001/.01", "001.01"),  # Will be converted
        ("001/.0.1", "001.0.1"), # Will be converted
        ("001/01", "001/01"),    # Won't be converted (no dot after slash)
        ("001.01", "001.01")     # Won't be converted
    ]
    
    print("\nConversion examples:")
    print("{:<15} {:<15} {:<10}".format("Before", "After", "Changed?"))
    print("-" * 45)
    for before, after in examples:
        converted = convert_dewey_format(before)
        print("{:<15} {:<15} {:<10}".format(
            before,
            converted,
            "Yes" if before != converted else "No"
        ))

def process_batch(solr, query, start, batch_size):
    """Process a batch of documents and return count updated"""
    results = solr.search(query, rows=batch_size, start=start)
    if not results:
        return 0

    updates = []
    for doc in results.docs:
        doc_id = doc.get('id')
        if not doc_id:
            continue
        
        update_doc = {"id": doc_id}
        needs_update = False
        
        # Process all Dewey fields
        for field in ['dewey-full', 'dewey-raw', 'dewey-search']:
            if field in doc:
                old_value = doc[field]
                if isinstance(old_value, list):
                    new_values = []
                    for v in old_value:
                        if isinstance(v, str):
                            converted = convert_dewey_format(v)
                            if converted != v:
                                new_values.append(converted)
                                needs_update = True
                            else:
                                new_values.append(v)
                        else:
                            new_values.append(v)
                    if needs_update:
                        update_doc[field] = {"set": new_values}
                elif isinstance(old_value, str):
                    converted = convert_dewey_format(old_value)
                    if converted != old_value:
                        update_doc[field] = {"set": converted}
                        needs_update = True
        
        if needs_update:
            updates.append(update_doc)

    if updates:
        try:
            solr.add(updates)
            return len(updates)
        except Exception as e:
            print(f"  Error updating batch: {e}")
            return 0
    return 0

def main():
    # Connect to Solr
    solr = pysolr.Solr('http://172.17.45.134:8983/solr/biblio', always_commit=False)

    # Count records with slashes in Dewey numbers
    print("\nSearching for records with / in Dewey numbers...")
    total_records = count_slash_records(solr)
    
    if total_records == 0:
        print("No records found with / in Dewey numbers")
        return
    
    print(f"\nFound {total_records} records with / in Dewey numbers")
    
    # Show conversion examples
    show_conversion_examples()
    
    # Get user confirmation
    confirm = input("\nDo you want to proceed with updating these records? (yes/no): ").lower().strip()
    if confirm != 'yes':
        print("Operation cancelled")
        return

    # Configure batch processing
    batch_size = 500
    total_updated = 0
    query = 'dewey-full:*/* OR dewey-raw:*/* OR dewey-search:*/*'
    
    print(f"\nStarting update of {total_records} records in batches of {batch_size}...")
    
    # Process in batches
    start = 0
    try:
        while start < total_records:
            batch_updated = process_batch(solr, query, start, batch_size)
            total_updated += batch_updated
            start += batch_size
            
            # Print progress
            print(f"Processed: {min(start, total_records)}/{total_records} | Updated: {total_updated}", end='\r')
            
            # Periodic confirmation
            if start % (batch_size * 10) == 0 and start < total_records:
                confirm = input(f"\nProcessed {start} records. Continue? (yes/no): ").lower().strip()
                if confirm != 'yes':
                    print("\nUpdate stopped by user")
                    break

        # Final commit
        solr.commit()
        print(f"\n\nUpdate completed. Total records updated: {total_updated}")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted. Committing completed updates...")
        solr.commit()
        print(f"Saved changes up to record {start}. Total updated: {total_updated}")
    except Exception as e:
        print(f"\nError during processing: {e}")
        print("Attempting to commit completed updates...")
        solr.commit()
        print(f"Saved changes up to record {start}. Total updated: {total_updated}")

if __name__ == "__main__":
    main()
