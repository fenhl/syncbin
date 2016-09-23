if which diskspace &> /dev/null; then
    echo `diskspace --zsh` 2> /dev/null
else
    echo '[disk: unknown]'
fi
