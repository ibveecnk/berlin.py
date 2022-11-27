# berlin.py
A discord bot written in python using discord.py

## Table of content
- [berlin.py](#berlinpy)
  - [Table of content](#table-of-content)
  - [Information on getting started](#information-on-getting-started)
    - [Logging](#logging)
  - [Running the bot](#running-the-bot)
    - [Install requirements/dependencies](#install-requirementsdependencies)
    - [Setup env file](#setup-env-file)
    - [Start the bot](#start-the-bot)
  - [Planned features](#planned-features)


## Information on getting started
### Logging
By default the bot is configured to write the log to a `discord.log` file in the root of the project directory. To access the logger from within a module, the logger is exposed as the `logger` property of the `bot` instance.

Example (within module):
```python
@commands.command()
async def example(self, context: commands.Context):
    self.bot.logger.info("Here you can write to the logger.")
```

## Running the bot
### Install requirements/dependencies
```shell
pip install -r requirements.txt
```

### Setup env file
- Copy `.env.dist` to `.env`
- Edit the parameters (e.g. TOKEN, etc.)

### Start the bot
```shell
python main.py
```

## Planned features
- [x] automatic reloading of modules (reload command)
- [ ] docker image for easy deploying
- [ ] music features
