# Mieszkaniobot

### An assistant in finding a flat for rental on OLX

The code is almost 2 years old and it might not work properly due to updates to OLX site. There are also things that I would implement differently now, but what matters is that it got the job done and helped me and a couple of other people.

## The problem and the solution

Finding a flat might be a tedious task due to high competition and having to keep up with new postings.

Mieszkaniobot was implemented to make the process easier. It periodically checks if any new flat rental offers have appeared, and if so it sends Telegram messages to specified chats with the URLs of the new postings.

This way there's no need to manually browse through the list of flats, and the notifications about new postings make it easy to contact renters quickly.

## Running

In the root of the repository there should be a `.env` file with the following variables set:
- `BOT_TOKEN`
- `CHAT_IDS`: JSON list
- `LOG_CHAT_ID`
- `SOURCES`: JSON list of URLs to the OLX sites with (filtered) flat rental offers

### Build

```
docker build -t mieszkaniobot .
```

### Run

```
docker run --env-file .env mieszkaniobot
```

To have the URLs of the visited rental offers persisted:

```
touch visited.txt
docker run \
  --env-file .env \
  -v "$(pwd)"/visited.txt:/home/mieszkaniobot/visited.txt \
  mieszkaniobot
```
