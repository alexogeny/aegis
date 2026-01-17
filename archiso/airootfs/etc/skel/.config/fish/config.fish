# Aegis Linux - Fish Configuration
# =============================================================================

# Remove greeting
set -g fish_greeting

# Environment variables
set -gx EDITOR nvim
set -gx VISUAL nvim

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

# Git abbreviations
abbr -a ga 'git add'
abbr -a gc 'git commit'
abbr -a gp 'git push'
abbr -a gpl 'git pull'
abbr -a gs 'git status'
abbr -a gd 'git diff'
abbr -a gl 'git log --oneline'

# Initialize Starship prompt
if type -q starship
    starship init fish | source
end

# Initialize zoxide
if type -q zoxide
    zoxide init fish | source
end

# Welcome message for TTY
if not set -q DISPLAY; and not set -q WAYLAND_DISPLAY
    echo "Welcome to Aegis Linux"
    echo "Run 'Hyprland' to start the desktop environment"
end
