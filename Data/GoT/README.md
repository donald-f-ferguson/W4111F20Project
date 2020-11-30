# Game of Thrones Data

- The datasets come from the GitHub project [Game of Thrones Datasets and Visualizations](https://github.com/jeffreylancaster/game-of-thrones).


- The [README](https://github.com/jeffreylancaster/game-of-thrones/blob/master/README.md) for the project explains the
datasets, visualizations, etc.


- The project's datasets are in JSON format. I wrote some simple Python programs that read the JSON files
and produce CSV files that you can load into MySQL.


- The files are:
    - characters: Basic information about characters in the story
        - id - An identifier. 
        - characterName - The name of the character.
        - characterLink - (Broken) link to information about the character in IMDB.
        - actorName - Name of actor portraying the character.
        - actorLink - Relative link to info about the character in IMDB.
        - character_id - A unique ID for the character entry.
        - royal - "True" or "False" if the character is royalty.
        - characterImageThumb, characterImageFull - URLs to images for the character.
        - kingsGuard - "True" or "False" depending on whether or not the character was in the Kingsguard.
    -character_actors: Mapping of character names to actors
        - id
        - characterName
        - actorName
        - actorLink
        - Season - Season in which the character played the actor, if specified.
    - character_relationshps: Relationships/interactions between characters based on various JSON files.
        - id
        - character_id - The ID of the source character in the relationship.
        - characterName - The name of the source character in the relationship.
        - label - Indicates the type of relationships, e.g. "parents," "siblings", "killedBy," ... ...
        - The name of the target character.
    - episodes: Information about episodes. Columns ave the obvious meanings.
    - groups:
        - id
        - groupName: The name of the group.
        - character: The name of the character in the group.    
    - locations:
        - id
        - location - The name of the location.
        - sublocation - The name of a sublocation within the larger location.   
    - scenes:
        - id
        - seasonNumber, episodeNumber have the obvious meaning.
        - sceneNo is the order of the scene in an episode. An episode is a sequence of scenes.
        - sceneStart, sceneEnd - Offsets in the episode time when the scene started and ended.
        - location, sublocation for the scene.
        - greensight, warg, flashback indicate whether the scene is a flashbach, the character was a warg
        or the scene was a greensight vision.
    - scenes_characters: 
        - id
        - seasonNum, episodeNum, sceneNum
        - characterName
        

- Successfully using the files requires:
    - Data cleanup, normalization, constraints, etc.
    - Creation of views that support common analysis and reporting scenarios.