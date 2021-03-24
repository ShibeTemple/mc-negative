# Minecraft Negative

Compares a Minecraft world against its younger self to create a negative of the differences, consisting typically of player actions like player structures and blocks removed from the world. We call these worlds Pre and Post. The Pre world could be a backup or a blank world generated with the same seed in the same Minecraft version. The program takes the differences between post and pre, then transposes them on a new world. This program was created with the intention of providing a way to essentially 'upgrade' a pre-existing Minecraft world to a newer version of Minecraft. Note: Currently does not support upgrading a pre-1.13 world past 1.13 due to data differences. Supports 1.16 to 1.17 and so on, however.

## Example:

`myworld` is a 1.12 map with player content. `world-pre` is a newly created 1.12 world with the same seed as `myworld`. This program will compare the differences between those two and place them onto the 1.16 `world-new` map, exported as `world-export`.

Usage:
```
python negative.py world-pre myworld world-new world-export -t 12
```

## Notes:

```
python negative.py PRE POST NEW EXPORT
```

This program does not modify the 'pre', 'post' or 'new' worlds. It only creates an output world, which consists of the differences of 'pre' & 'post' transposed on 'new'.

## Command-line options:

| Argument | Description |
| --- | --- |
| `-v`<br/> or<br/> `-verbose` | Enables verbose logging. **NOTE:** Slows down execution time tremendously. |
| `-b`<br/> or<br/> `-bedrock` | Forces the program to check the bedrock layer (y=0) of blocks when running through every chunk. Normally excluded for efficiency. |
| `-t 1`<br/> or<br/> `-threads 1` | Number of region files to compare simultaneously. Each region file is assigned its own thread. Default is 1.  |

## Tested MC Versions

| Old Version | New Version | Successful | Notes |
| --- | --- | --- | --- |
| 1.12 | 1.12 | yes | simple data migration test |
| 1.16 | 1.17 (21w11a) | yes | relevant world upgrade test |
| 1.12 | 1.16 | no, see open issue regarding this | version jump test, 1.13 Flattening issue |
