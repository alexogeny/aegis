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
abbr -a gco 'git checkout'
abbr -a gsw 'git switch'
abbr -a gb 'git branch'
abbr -a gst 'git stash'
abbr -a lg 'lazygit'

# GitHub/GitLab CLI abbreviations
abbr -a ghpr 'gh pr'
abbr -a ghis 'gh issue'
abbr -a ghdash 'gh dash'
abbr -a glmr 'glab mr'
abbr -a glis 'glab issue'

# Docker abbreviations
abbr -a dps 'docker ps'
abbr -a dpa 'docker ps -a'
abbr -a di 'docker images'
abbr -a dex 'docker exec -it'
abbr -a dc 'docker compose'
abbr -a dcu 'docker compose up -d'
abbr -a dcd 'docker compose down'
abbr -a dcl 'docker compose logs -f'

# Kubernetes abbreviations
abbr -a k 'kubectl'
abbr -a kgp 'kubectl get pods'
abbr -a kgs 'kubectl get svc'
abbr -a kgd 'kubectl get deployments'
abbr -a kaf 'kubectl apply -f'
abbr -a kdf 'kubectl delete -f'
abbr -a klog 'kubectl logs -f'
abbr -a kex 'kubectl exec -it'

# Initialize Starship prompt
if type -q starship
    starship init fish | source
end

# Initialize zoxide (smart cd)
if type -q zoxide
    zoxide init fish | source
end

# Initialize direnv (per-directory environments)
if type -q direnv
    direnv hook fish | source
end

# GitHub CLI completions
if type -q gh
    gh completion -s fish | source 2>/dev/null
end

# GitLab CLI completions
if type -q glab
    glab completion -s fish | source 2>/dev/null
end

# kubectl completions
if type -q kubectl
    kubectl completion fish | source 2>/dev/null
end

# Welcome message for TTY
if not set -q DISPLAY; and not set -q WAYLAND_DISPLAY
    echo "Welcome to Aegis Linux"
    echo "Run 'Hyprland' to start the desktop environment"
end
