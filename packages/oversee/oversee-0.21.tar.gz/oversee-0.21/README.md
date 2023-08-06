# Oversee
Helps oversee your Ubuntu OS!

Want to install CLion with one command? Or Google Chrome? Or all of your development software? How about a cleaner and easier way to define your .bash_aliases? Or a way to
sync all of your jetbrains settings? This package will help!


## Installation
```
pip install oversee
oversee --help
```

Place an `.oversee.yaml` in your home directory (ex. `~/.oversee.yaml`). See `examples/` for some examples!

## Example Usage
```
# Install a package
oversee install clion

# Export your bash aliases to ~/.bash_aliases
oversee export
```

## Roadmap
- [x] Added jetbrains settings sync support
- [x] Make environments work
- [x] Add project management components (make releases)
- [x] Autocomplete functionality
- [x] Add list commands using decorator
- [x] Add jetbrains .gitignore command
