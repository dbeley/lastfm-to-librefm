# lastfm-to-librefm

Simple python script to export lastfm scrobbles to a librefm account.

## Instructions

- Be sure to have the credentials for a lastfm account and your librefm account, as well as an API key and an API secret for lastfm (get them at https://www.last.fm/api/account/create).
- Download the [lastfm-scraper](https://github.com/dbeley/lastfm-scraper) repository.
- In the lastfm-scraper folder, fill your credentials in config.ini (take config_sample.ini as an example)
- Run the lastfm-complete_timeline.py script (The timeline will be exported in a folder called "Exports") :

```
python lastfm-complete_timeline.py -u USERNAME
# You can also extract timelines of several lastfm accounts
python lastfm-complete_timeline.py -u USERNAME1,USERNAME2
```

- Download the [lastfm-to-librefm](https://github.com/dbeley/lastfm-to-librefm) repository.
- In the lastfm-to-librefm folder, fill your librefm credentials in config.ini (config_sample.ini as an example).
- Run the lastfm-to-librefm.py script (Change the path accordingly) :

```
python lastfm-to-librefm.py -f timeline_USERNAME.txt
# You can also transfer several timelines to your librefm account
python lastfm-to-librefm.py -f timeline_USERNAME1.txt,timeline_USERNAME2.txt
```

## Requirements

- pandas
- pylast
