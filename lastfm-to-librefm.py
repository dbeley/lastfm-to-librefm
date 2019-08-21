import configparser
import pylast
import os
import time
import logging
import argparse
import pandas as pd
from pathlib import Path

logger = logging.getLogger()
BEGIN_TIME = time.time()
LIBREFM_SESSION_KEY_FILE = "session_key.librefm"


def librefmconnect():
    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config["librefm"]["username"]
    password = pylast.md5(config["librefm"]["password"])

    librefm = pylast.LibreFMNetwork(username=username, password_hash=password)
    return librefm


def session(network, key_file):
    if not os.path.exists(key_file):
        skg = pylast.SessionKeyGenerator(network)
        url = skg.get_web_auth_url()

        logger.info(
            "Please authorize the scrobbler "
            "to scrobble to your account: %s\n" % url
        )
        import webbrowser

        webbrowser.open(url)

        while True:
            try:
                session_key = skg.get_web_auth_session_key(url)
                fp = open(key_file, "w")
                fp.write(session_key)
                fp.close()
                break
            except pylast.WSError:
                time.sleep(1)
    else:
        session_key = open(key_file).read()

    network.session_key = session_key


def main():
    args = parse_args()

    # Check if file argument is present
    if not args.file:
        logger.error(
            "Use the -f/--file argument to input a file containing a timeline."
        )
        exit()
    files = [x.strip() for x in args.file.split(",")]

    # Concatenate every file into a pandas dataframe
    df = None
    for file in files:
        logger.info("Processing file %s.", file)
        df_initial, df = df, pd.read_csv(file, delimiter="\t")
        df = pd.concat([df, df_initial], ignore_index=True, sort=True)

    # Sort by timestamp
    df = df.sort_values(by=["Timestamp"])
    logger.info("%s records found.", df.shape[0])

    # Load checkpoint if exists
    last_checkpoint_file = Path("last_checkpoint")
    if last_checkpoint_file.is_file():
        with open(last_checkpoint_file, "r") as f:
            last_checkpoint = f.read()
        logger.info("Checkpoint found. Last timestamp : %s.", last_checkpoint)
    else:
        last_checkpoint = None

    # Keep only records where timestamp > last_checkpoint
    if last_checkpoint:
        df = df[df.Timestamp.astype(int) > int(last_checkpoint)]
        logger.info("%s records kept.", df.shape[0])

    logger.info("Connecting to librefm.")
    librefm = librefmconnect()
    session(librefm, LIBREFM_SESSION_KEY_FILE)

    nb_line = df.shape[0]
    index = 0
    for _, row in df.iterrows():
        index += 1
        logger.info(
            f"%s/%s - Sending %s - %s (%s) : %s to librefm.",
            index,
            nb_line,
            row["Artist"],
            row["Title"],
            row["Album"],
            row["Timestamp"],
        )
        nb_tries = 0
        while True:
            if nb_tries > 5:
                break
            try:
                if pd.isna(row["Album"]):
                    librefm.scrobble(
                        artist=row["Artist"],
                        title=row["Title"],
                        timestamp=row["Timestamp"],
                    )
                else:
                    librefm.scrobble(
                        artist=row["Artist"],
                        title=row["Title"],
                        timestamp=row["Timestamp"],
                        album=row["Album"],
                    )
                break
            except Exception as e:
                logger.error("Error scrobbling : %s. Retrying.", e)
                nb_tries += 1
        # Write checkpoint at each scrobble
        timestamp = row["Timestamp"]
        with open("last_checkpoint", "w") as f:
            f.write(str(timestamp))

    logger.info("Runtime : %.2f seconds." % (time.time() - BEGIN_TIME))


def parse_args():
    format = "%(levelname)s :: %(message)s"
    parser = argparse.ArgumentParser(description="lastfm2librefm script.")
    parser.add_argument(
        "--debug",
        help="Display debugging information.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-f",
        "--file",
        help="CSV file containing scrobbles from lastfm.",
        type=str,
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel, format=format)
    return args


if __name__ == "__main__":
    main()
