# IMDB Data

- The datasets come from the downloadable [IMDB datasets.](https://www.imdb.com/interfaces/) The site explains the
data files and their contents.


- This directory contains one sub-directory for each of the IMDB data files.
    - Even in compressed format, some of the files are enormous. For example, the compressed form of title.principals.tsv
    is 350 MB. The uncompressed format is 1.9 GB. The files are too large for GitHub and are unworkable.
    - Each subdirectory contains partitions of the original file into files that are 50 MB or less.
    
    
- Working with this data requires:
    - Creating the tables. There is an [SQL file](Data/IMDB/imdb_schema.sql) that creates the necessary tables.
    - Loading the TSV files data into the appropriate tables.
    - Some schema improvement and data model redesign.
    - Creation if indexes. 