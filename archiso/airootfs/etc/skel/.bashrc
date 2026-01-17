# Aegis Linux - Bash Configuration
# =============================================================================

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# History settings
HISTSIZE=10000
HISTFILESIZE=20000
HISTCONTROL=ignoreboth:erasedups
shopt -s histappend

# Check window size after each command
shopt -s checkwinsize

# Enable programmable completion
if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
fi

# Aliases
alias ls='eza --color=auto --icons'
alias ll='eza -la --icons'
alias la='eza -a --icons'
alias lt='eza --tree --icons'
alias grep='grep --color=auto'
alias cat='bat --style=plain'
alias vim='nvim'
alias vi='nvim'

# Safety aliases
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Aegis-specific aliases
alias security-check='sudo aegis-hardening-check'
alias aa-status='sudo aa-status'
alias fw-status='sudo nft list ruleset'
alias audit-log='sudo journalctl -f _TRANSPORT=audit'

# Initialize Starship prompt
eval "$(starship init bash)"

# Initialize zoxide
eval "$(zoxide init bash)"

# Welcome message
if [[ -z "$DISPLAY" ]] && [[ -z "$WAYLAND_DISPLAY" ]]; then
    echo "Welcome to Aegis Linux"
    echo "Run 'Hyprland' to start the desktop environment"
fi
