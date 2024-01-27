
1. Rebuild the schema and database
```
rm db/relevation.db
python manage.py migrate --run-syncdb
```
2. Prepare collections (for retrieved documents)
For efficiency, this system would read the file once a time.
Thus, only one line of document should be stored in a file; 
the filename refers to document identified.

- We use the parsed 10K collections, and you can use `split_corpus.py` to pool your docs. Please download [here](#) or cfda server:``/home/ythsiao/output``.
- The documents will output in the `documents` folder.
```
for file in raw_data/*/10-K/*jsonl;do
    python3 preprocess/split_data.py \
        --input_jsonl $file \   # the jsonl with entire document.
        --output_dir documents/ # all documents would output here.
done
```

3. Start server
```
python manage.py runserver
```

4. Setup and upload queries and retreived results
See the exampels query and result in this repo.
- query file: [query.jsonl](example/query.jsonl)
- result file: [qresult.txt](testing/qresult.txt)

The extracted query files of MD&A can be founded in `/home/ythsiao/mda`.
