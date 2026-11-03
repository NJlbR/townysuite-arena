import re

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's add a debug log or just force the title if the config string doesn't contain the unicode chars for some reason.
# But actually, looking at the user's screenshot...
# The title in their screenshot is exactly "Чертежи и постройки" in dark gray!
# WHICH MEANS, their config STILL has the OLD title: `title: "&8Чертежи и постройки"`.
# The plugin didn't overwrite the old config correctly because the user didn't delete it, OR they deleted it and the old JAR was loaded?
# No, if the title is &8, it means it's falling back to the default `getString("gui.title", "&8Чертежи и постройки")`.
# WHY would it fall back? Because `gui.title` doesn't exist in their config!
# Why doesn't it exist? Because `saveDefaultConfig()` DOES NOT OVERWRITE if the file exists!
# The user probably didn't delete `config.yml` properly.
