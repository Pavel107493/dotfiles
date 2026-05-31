# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi


# nitch
# pokemon-colorscripts --random
# figlet -f small " Arch Linux"

# Path to your Oh My Zsh installation.
# export ZELLIJ_AUTO_EXIT="true"
export ZSH="$HOME/.oh-my-zsh"
export LANG=en_US.UTF-8
export LANG=ru_RU.UTF-8
export LC_ALL=en_US.UTF-8
ZSH_THEME="powerlevel10k/powerlevel10k"  #git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k"
# ZSH_THEME="bira" #ZSH_THEME="powerlevel10k/powerlevel10k" ZSH_THEME="agnoster" "bira", "amuse"
_comp_options+=(globdots) # фикс отображения скрытых файлов

###############
### Плагины ###
###############

plugins=(
git # показывает статус git в текущей папке
zsh-autosuggestions # Автокомплит по истории 
zsh-syntax-highlighting # Подсветка синтаксиса
z # быстрое перемещение по папкам
# zsh-autocomplete
archlinux
)

# Использование oh-my-zsh
source $ZSH/oh-my-zsh.sh
# Установка oh-my-zsh
# sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
# sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"


# Фикс prompt для Wayland/Hyprland
PROMPT_EOL_MARK=""
prompt_opts=(percent subst)

# Мои алиасы
alias inst="sudo pacman -S"
alias insty="yay -S"
alias remo="sudo pacman -R"
alias up="cd ../"
alias ls="ls --color=auto"
alias la="la --color=auto"
alias rm="trash-put"
alias rp="realpath"
alias proxy10808="env https_proxy=http://127.0.0.1:10808"
alias gitkraken="gitkraken --force-device-scale-factor=0.8 --no-deprecation"

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
