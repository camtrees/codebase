def df_print_examples(df):
    """Some DataFrame print examples."""
    # Print the column names
    my_pretty_print(df.columns)

    # Print the first 3 records
    my_pretty_print(df.head(3))

    # Print the dataframe as a string
    print(df.to_string())


def df_convert_to_cvs(df):
    """Convert DataFrame to CVS format."""
    return df.to_csv(index=False)
