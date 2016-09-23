if which batcharge &> /dev/null; then
    echo `batcharge --zsh` 2> /dev/null
else
    echo '[battery: unknown]'
fi
