# Contributing to DPY-Ticket-Bot
I love all input, whether its issues or pull requests!

### This project is solely ran through Github
Github is used to host code, to track issues and feature requests, as well as accept pull requests.

### Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

---

## Report bugs using Github's [issues](https://github.com/Skelmis/DPY-Ticket-Bot/issues)
I use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/Skelmis/DPY-Ticket-Bot/issues/new); it's that easy!

---

## Fork & Pull Request to add new code
I love new code for this project, I love seeing it grow. However, there is a process to be followed.

> Fork `master` branch & get coding
>
> Whenever ready, create a pull request & ask for a review from `Skelmis`
>
> Code will be reviewed, and once it is at a stage where it is approved it will be merged

*I have the right to accept/deny any good I feel does not add to this project*

---

## Use a Consistent Coding Style
- Tabs should be 4 spaces for indentation
- Where applicable, code should be documented. For implementation see the below Documentaion sections
- Where code gets excessive, functional programming ideas should come into play for readability
- `return` statements are prefered within conditionals when checking whether to continue with processing or not
For example:
```python
if not condtion:
    # This means we should not process the rest of the command
    await ctx.send("You are missing perms, an argument, etc")
    return

# We should process the rest of the command here
```
Is preferred over:
```python
if not condtion:
    # This means we should not process the rest of the command
    await ctx.send("You are missing perms, an argument, etc")
else:
    # We should process the rest of the command
```

### Function Documentation
- All new functions should be documented in accordance with [these](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard) conventions

### Command Documentation
##### Required
- `name` -> attribute with the name of the command
- `description` -> A short description of what this command does, do not cover how it is implemented.
##### Optional
- `aliases` -> For use if the command has aliases
- `usage` -> If the command takes arguments, this is **Required**. Format should include required arguments surrounded by `<>` and optional arguments surrounded by `[]`

Example:
```python
@bot.command(
    name="echo",
    description="Repeat some text back using the bot.",
    usage="<channel> <message>",
)
@commands.guild_only()
@commands.is_owner()
async def echo(ctx, channel: discord.TextChannel, *, content):
    await ctx.message.delete()
    embed = discord.Embed(
        description=content, color=0x808080, timestamp=ctx.message.created_at
    )
    embed.set_author(name=ctx.guild.me.display_name, icon_url=ctx.guild.me.avatar_url)
    await channel.send(embed=embed)
```
