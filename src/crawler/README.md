## Crawler

Package can crawl over Yad-2 website

### How-To

- Install: `pip install src/crawler`
- Run: `python -m crawler`
- Usage:<br>
```
python -m crawler --help
usage: __main__.py [-h] [-p PROPERTIES_PER_FILE] [-e ENGINE] [-m MAX_WORKERS]

Yad2 Crawler Program

optional arguments:
  -h, --help            show this help message and exit
  -p PROPERTIES_PER_FILE, --properties_per_file PROPERTIES_PER_FILE
                        Set how many properties to collect for each file.
  -e ENGINE, --engine ENGINE
                        Run crawler on given engine.
  -m MAX_WORKERS, --max_workers MAX_WORKERS
                        Program threads number.
```

Notes: Program currently run under python3 only.
